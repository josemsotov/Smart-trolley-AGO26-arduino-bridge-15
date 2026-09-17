"""Temporary suspended-bench test only; not an operational collision monitor.

Raw frontal sensor thresholds, not footprint clearances. Default is dry-run.
The normal mux must be stopped before --armed (enforced publisher count).
"""
import argparse, json, math, time
from pathlib import Path
import numpy as np
import rclpy
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data
from geometry_msgs.msg import Twist
from sensor_msgs.msg import LaserScan, Image
from std_msgs.msg import String
from bench_stop_latch import advance_latch

p=argparse.ArgumentParser();p.add_argument('--armed',action='store_true');a=p.parse_args()
rclpy.init();n=Node('bench_obstacle_stop')
pub=n.create_publisher(Twist,'/cmd_vel' if a.armed else '/bench_obstacle/dry_command',1)
state={'scan_t':0.,'depth_t':0.,'motor_t':0.,'front':None,'depth':None,
       'scan_fraction':0.,'depth_fraction':0.,'rpm':0.,'pwm':0.}
rows=[];latch=None;start=time.monotonic();drive_start=None;last_print=0.;clear_since=None
def scan(m):
    sector=[r for i,r in enumerate(m.ranges) if abs((m.angle_min+i*m.angle_increment+math.pi)%(2*math.pi)-math.pi)<math.radians(30)]
    valid=[r for r in sector if math.isfinite(r) and m.range_min<=r<=m.range_max]
    if m.header.frame_id!='base_laser':return
    state.update(scan_t=time.monotonic(),front=min(valid) if valid else None,
                 scan_fraction=len(valid)/max(1,len(sector)))
def depth(m):
    if m.encoding not in ('16UC1','32FC1') or m.header.frame_id!='camera_depth_optical_frame':return
    dtype=np.dtype(('>' if m.is_bigendian else '<')+('u2' if m.encoding=='16UC1' else 'f4'))
    image=np.ndarray((m.height,m.width),dtype=dtype,buffer=m.data,strides=(m.step,dtype.itemsize))
    roi=image[m.height//3:2*m.height//3,m.width//3:2*m.width//3].astype(float)
    if m.encoding=='16UC1':roi/=1000
    valid=roi[np.isfinite(roi)&(roi>0)]
    state.update(depth_t=time.monotonic(),depth=float(valid.min()) if valid.size else None,
                 depth_fraction=valid.size/max(1,roi.size))
def motor(m):
    try:
        d=json.loads(m.data)
        # Bridge publishes key/value T text, not JSON on this topic.
    except ValueError:
        d=dict(x.split('=',1) for x in m.data.split() if '=' in x)
    try:state.update(motor_t=time.monotonic(),rpm=max(abs(float(d[k])) for k in ('Lrpm','Rrpm')),
                     pwm=max(abs(float(d[k])) for k in ('Lpwm','Rpwm')),motor_raw=m.data)
    except (KeyError,ValueError,TypeError):pass
def stop_request(m):
    global latch
    state['stop_request_payload']=m.data
    print('STOP_REQUEST '+repr(m.data),flush=True)
    latch=latch or 'operator_request'
def field(m):
    global latch
    try:
        d=json.loads(m.data)
        if d.get('emergency_latched') or d.get('effective_mode')=='EMERGENCY_STOP':latch=latch or 'emergency'
    except ValueError:latch=latch or 'invalid_field_state'
n.create_subscription(LaserScan,'/scan',scan,qos_profile_sensor_data)
n.create_subscription(Image,'/camera/depth/image_raw',depth,1)
n.create_subscription(String,'/motor_status',motor,10)
n.create_subscription(String,'/field/mode_request',stop_request,10)
n.create_subscription(String,'/stadia/control',stop_request,10)
n.create_subscription(String,'/field/state',field,10)
out=Path('/home/josemsotov/robot_calibration')/('obstacle_'+('armed_' if a.armed else 'dry_')+time.strftime('%Y%m%d_%H%M%S')+'.json')
out.parent.mkdir(exist_ok=True)
try:
    while time.monotonic()-start< (55 if a.armed else 16):
        rclpy.spin_once(n,timeout_sec=.02)
        now=time.monotonic();t=now-start
        reason=None
        if now-state['scan_t']>.35 or now-state['depth_t']>.5 or now-state['motor_t']>.7:reason='stale_sensor_or_motor'
        elif state['front'] is None or state['depth'] is None or state['scan_fraction']<.5 or state['depth_fraction']<.5:reason='invalid_or_insufficient_data'
        elif state['front']<.8 or state['depth']<.8:reason='obstacle'
        elif state['rpm']>120:reason='rpm_limit'
        if a.armed and n.count_publishers('/cmd_vel')!=1:reason='multiple_cmd_publishers'
        if drive_start is None:
            clear=(reason is None and state['front']>=1.2 and state['depth']>=1.2 and state['pwm']==0 and state['rpm']==0)
            clear_since=(clear_since or now) if clear else None
            if t>=12:
                if not clear_since or now-clear_since<2:latch=latch or 'preflight_not_clear'
                elif not latch:
                    drive_start=now
                    print('MOVING' if a.armed else 'DRY_READY',flush=True)
        else:
            latch=advance_latch(latch,reason,now-drive_start)
        speed=0. if latch or drive_start is None else .125*min(1,(now-drive_start)/2)
        msg=Twist();msg.linear.x=speed;pub.publish(msg)
        rows.append(dict(t=t,command=speed,latch=latch,reason=reason,**state))
        if now-last_print>=1:
            print(json.dumps(dict(t=round(t,1),command=round(speed,3),latch=latch,reason=reason,front=state['front'],depth=state['depth'],rpm=state['rpm'],pwm=state['pwm'])),flush=True)
            last_print=now
        if latch and drive_start is None and t>14:break
        time.sleep(.025)
finally:
    for _ in range(10):pub.publish(Twist());time.sleep(.05)
    out.write_text(json.dumps(rows));print('SAVED '+str(out),flush=True)
    n.destroy_node();rclpy.shutdown()
