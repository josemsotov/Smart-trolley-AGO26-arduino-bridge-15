"""Read-only simultaneous LaserScan/TF audit; never publishes motion commands."""
import json
import math
import time

import rclpy
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data
from rclpy.time import Time
from sensor_msgs.msg import LaserScan
from tf2_ros import Buffer, TransformListener


def main():
    rclpy.init()
    node = Node('audit_dual_lidar')
    buffer = Buffer()
    listener = TransformListener(buffer, node)
    stats = {}

    def receive(topic, msg):
        now = time.monotonic()
        valid = [r for r in msg.ranges if math.isfinite(r)
                 and msg.range_min <= r <= msg.range_max]
        entry = stats.setdefault(topic, {'messages': 0, 'first': now})
        entry.update(messages=entry['messages'] + 1, last=now,
                     frame=msg.header.frame_id, points=len(msg.ranges),
                     valid=len(valid), minimum_m=min(valid) if valid else None)

    subs = [node.create_subscription(
        LaserScan, topic, lambda msg, t=topic: receive(t, msg),
        qos_profile_sensor_data) for topic in ('/scan', '/scan_lower')]
    try:
        end = time.monotonic() + 12
        while time.monotonic() < end:
            rclpy.spin_once(node, timeout_sec=0.2)
        passed = True
        for topic in ('/scan', '/scan_lower'):
            entry = stats.setdefault(topic, {'messages': 0})
            if entry['messages'] < 20:
                passed = False
                continue
            entry['hz'] = (entry['messages'] - 1) / (entry['last'] - entry['first'])
            entry['age_s'] = time.monotonic() - entry['last']
            try:
                tf = buffer.lookup_transform('base_link', entry['frame'], Time()).transform
                entry['translation'] = [tf.translation.x, tf.translation.y, tf.translation.z]
                entry['quaternion_xyzw'] = [tf.rotation.x, tf.rotation.y, tf.rotation.z, tf.rotation.w]
            except Exception as exc:
                entry['tf_error'] = str(exc)
                passed = False
            passed = passed and entry['age_s'] < 1 and entry['valid'] > 0
        print(json.dumps({'passed': passed, 'scans': stats}, indent=2), flush=True)
        return 0 if passed else 1
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    raise SystemExit(main())
