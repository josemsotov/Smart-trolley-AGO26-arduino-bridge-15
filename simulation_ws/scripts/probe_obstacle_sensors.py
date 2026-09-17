"""Passive 12-second ROS sensor audit. No publishers and no motor commands."""
import json, math, time
import numpy as np
import rclpy
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data
from sensor_msgs.msg import LaserScan, Image

rclpy.init()
n=Node('obstacle_sensor_passive_audit')
data={'scan_messages':0,'depth_messages':0}
def scan(m):
    vals=[x for x in m.ranges if math.isfinite(x) and m.range_min<=x<=m.range_max]
    front=[r for i,r in enumerate(m.ranges) if math.isfinite(r) and m.range_min<=r<=m.range_max and abs((m.angle_min+i*m.angle_increment+math.pi)%(2*math.pi)-math.pi)<math.radians(30)]
    data.update(scan_messages=data['scan_messages']+1,scan_frame=m.header.frame_id,
        scan_total=len(m.ranges),scan_valid=len(vals),scan_min=min(vals) if vals else None,
        angle_min=m.angle_min,angle_max=m.angle_max,
        front_min_m=min(front) if front else None,front_valid=len(front))
def depth(m):
    data.update(depth_messages=data['depth_messages']+1,depth_frame=m.header.frame_id,
                encoding=m.encoding,width=m.width,height=m.height)
    if m.encoding not in ('16UC1','32FC1'):return
    dtype=np.dtype(('>' if m.is_bigendian else '<')+('u2' if m.encoding=='16UC1' else 'f4'))
    a=np.ndarray((m.height,m.width),dtype=dtype,buffer=m.data,strides=(m.step,dtype.itemsize))
    roi=a[m.height//3:2*m.height//3,m.width//3:2*m.width//3].astype(float)
    if m.encoding=='16UC1':roi/=1000
    valid=roi[np.isfinite(roi)&(roi>0)]
    data.update(depth_center_valid_fraction=float(valid.size/roi.size),
        depth_center_min_m=float(valid.min()) if valid.size else None)
n.create_subscription(LaserScan,'/scan',scan,qos_profile_sensor_data)
n.create_subscription(Image,'/camera/depth/image_raw',depth,2)
try:
    end=time.monotonic()+12
    while time.monotonic()<end:rclpy.spin_once(n,timeout_sec=.2)
    print(json.dumps(data),flush=True)
finally:
    n.destroy_node();rclpy.shutdown()
