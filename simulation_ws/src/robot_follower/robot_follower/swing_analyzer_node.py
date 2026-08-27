"""Kinect RGB golf-swing posture and tempo pilot using MediaPipe Pose."""
import json
import math
import time

import numpy as np
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from std_msgs.msg import String


def angle(a, b, c):
    ba = np.array([a.x - b.x, a.y - b.y])
    bc = np.array([c.x - b.x, c.y - b.y])
    denom = np.linalg.norm(ba) * np.linalg.norm(bc)
    if denom < 1e-6:
        return None
    return math.degrees(math.acos(float(np.clip(np.dot(ba, bc) / denom, -1, 1))))


def line_angle(a, b):
    return math.degrees(math.atan2(b.y - a.y, b.x - a.x))


class SwingAnalyzer(Node):
    def __init__(self):
        super().__init__('swing_analyzer')
        self.pub = self.create_publisher(String, '/swing/status', 10)
        self.create_subscription(String, '/swing/control', self.control_cb, 10)
        self.create_subscription(Image, '/camera/rgb/image_raw', self.image_cb, 2)
        self.recording = False
        self.started = None
        self.last_process = 0.0
        self.last_wrists = None
        self.last_wrist_time = None
        self.samples = []
        self.latest = {'state': 'ready', 'pose_visible': False}
        try:
            import mediapipe as mp
            self.mp = mp
            self.pose = mp.solutions.pose.Pose(
                static_image_mode=False,
                model_complexity=1,
                smooth_landmarks=True,
                min_detection_confidence=0.55,
                min_tracking_confidence=0.55,
            )
        except Exception as exc:
            self.pose = None
            self.latest = {'state': 'error', 'error': f'MediaPipe Pose: {exc}'}
        self.create_timer(0.5, self.publish_latest)

    def control_cb(self, msg):
        command = msg.data.strip().lower()
        if command == 'start':
            self.recording = True
            self.started = time.monotonic()
            self.samples = []
            self.last_wrists = None
            self.last_wrist_time = None
        elif command == 'stop':
            self.recording = False
            self.latest = self.summary()
            self.publish_latest()
        elif command == 'reset':
            self.recording = False
            self.samples = []
            self.latest = {'state': 'ready', 'pose_visible': False}

    def image_cb(self, msg):
        now = time.monotonic()
        if self.pose is None or now - self.last_process < 0.10:
            return
        self.last_process = now
        if msg.encoding.lower() == 'rgb8':
            rgb = np.frombuffer(msg.data, np.uint8).reshape(msg.height, msg.width, 3)
        elif msg.encoding.lower() == 'bgr8':
            bgr = np.frombuffer(msg.data, np.uint8).reshape(msg.height, msg.width, 3)
            rgb = bgr[:, :, ::-1]
        else:
            return
        result = self.pose.process(rgb)
        if not result.pose_landmarks:
            self.latest = {'state': 'recording' if self.recording else 'ready',
                           'pose_visible': False}
            return
        lm = result.pose_landmarks.landmark
        P = self.mp.solutions.pose.PoseLandmark
        ls, rs = lm[P.LEFT_SHOULDER], lm[P.RIGHT_SHOULDER]
        lh, rh = lm[P.LEFT_HIP], lm[P.RIGHT_HIP]
        lk, rk = lm[P.LEFT_KNEE], lm[P.RIGHT_KNEE]
        la, ra = lm[P.LEFT_ANKLE], lm[P.RIGHT_ANKLE]
        lw, rw = lm[P.LEFT_WRIST], lm[P.RIGHT_WRIST]
        shoulder_mid = ((ls.x + rs.x) / 2, (ls.y + rs.y) / 2)
        hip_mid = ((lh.x + rh.x) / 2, (lh.y + rh.y) / 2)
        spine_tilt = math.degrees(math.atan2(
            shoulder_mid[0] - hip_mid[0], hip_mid[1] - shoulder_mid[1]))
        wrist_mid = ((lw.x + rw.x) / 2, (lw.y + rw.y) / 2)
        wrist_speed = 0.0
        if self.last_wrists is not None and self.last_wrist_time is not None:
            dt = max(1e-3, now - self.last_wrist_time)
            wrist_speed = math.dist(wrist_mid, self.last_wrists) / dt
        self.last_wrists, self.last_wrist_time = wrist_mid, now
        sample = {
            't': 0.0 if self.started is None else now - self.started,
            'shoulder_tilt_deg': round(line_angle(ls, rs), 1),
            'hip_tilt_deg': round(line_angle(lh, rh), 1),
            'spine_tilt_deg': round(spine_tilt, 1),
            'left_knee_deg': round(angle(lh, lk, la) or 0.0, 1),
            'right_knee_deg': round(angle(rh, rk, ra) or 0.0, 1),
            'wrist_speed_norm_s': round(wrist_speed, 3),
        }
        self.latest = {'state': 'recording' if self.recording else 'ready',
                       'pose_visible': True, 'live': sample,
                       'sample_count': len(self.samples)}
        if self.recording:
            self.samples.append(sample)

    def summary(self):
        if not self.samples:
            return {'state': 'complete', 'pose_visible': False,
                    'error': 'No se capturaron muestras de pose'}
        peak = max(self.samples, key=lambda x: x['wrist_speed_norm_s'])
        shoulder_range = max(x['shoulder_tilt_deg'] for x in self.samples) - min(
            x['shoulder_tilt_deg'] for x in self.samples)
        hip_range = max(x['hip_tilt_deg'] for x in self.samples) - min(
            x['hip_tilt_deg'] for x in self.samples)
        duration = self.samples[-1]['t']
        return {'state': 'complete', 'pose_visible': True,
                'sample_count': len(self.samples), 'duration_s': round(duration, 2),
                'peak_time_s': round(peak['t'], 2),
                'peak_wrist_speed_norm_s': peak['wrist_speed_norm_s'],
                'shoulder_tilt_range_deg': round(shoulder_range, 1),
                'hip_tilt_range_deg': round(hip_range, 1),
                'finish_spine_tilt_deg': self.samples[-1]['spine_tilt_deg'],
                'note': 'Piloto corporal 2D; no mide impacto ni velocidad del palo.'}

    def publish_latest(self):
        self.pub.publish(String(data=json.dumps(self.latest)))


def main():
    rclpy.init()
    node = SwingAnalyzer()
    try:
        rclpy.spin(node)
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
