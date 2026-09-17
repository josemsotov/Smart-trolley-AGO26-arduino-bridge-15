"""Passive static scan recording; no command publishers."""
import json, math, time
from pathlib import Path
import rclpy
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data
from sensor_msgs.msg import LaserScan

rclpy.init()
n=Node('static_lidar_test')
start=time.monotonic()
rows=[]
out=Path('/home/josemsotov/robot_calibration')/('static_lidar_'+time.strftime('%Y%m%d_%H%M%S')+'.json')
out.parent.mkdir(exist_ok=True)
def cb(m):
    sectors={}
    for center in (0,90,180,270):
        vals=[float(r) for i,r in enumerate(m.ranges)
              if math.isfinite(r) and m.range_min<=r<=m.range_max
              and abs((math.degrees(m.angle_min+i*m.angle_increment)-center+180)%360-180)<=20]
        sectors[str(center)]=dict(valid=len(vals),minimum=min(vals) if vals else None)
    rows.append(dict(t=time.monotonic()-start,frame=m.header.frame_id,sectors=sectors,
        angle_min=m.angle_min,angle_increment=m.angle_increment,
        ranges=[float(r) if math.isfinite(r) else None for r in m.ranges]))
    if len(rows)==1:print('READY '+str(out)+' sectors='+json.dumps(sectors),flush=True)
    if len(rows)%10==0:out.write_text(json.dumps(rows))
n.create_subscription(LaserScan,'/scan',cb,qos_profile_sensor_data)
try:
    while time.monotonic()-start<120:rclpy.spin_once(n,timeout_sec=.2)
finally:
    out.write_text(json.dumps(rows))
    print('SAVED '+str(out)+' scans='+str(len(rows)),flush=True)
    n.destroy_node();rclpy.shutdown()
