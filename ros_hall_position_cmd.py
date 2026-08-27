#!/usr/bin/env python3
"""Drive until Hall pulse distance is reached, with a hard time limit."""

import argparse
import re
import time

import rclpy
from geometry_msgs.msg import Twist
from std_msgs.msg import String


COUNTS_RE = re.compile(r"\bHL=(\d+)\s+HR=(\d+)")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--speed", type=float, default=0.10)
    parser.add_argument("--target-pulses", type=float, default=5.3)
    parser.add_argument("--min-wheel-pulses", type=int, default=4)
    parser.add_argument("--timeout", type=float, default=3.0)
    args = parser.parse_args()

    rclpy.init()
    node = rclpy.create_node("hall_position_test")
    publisher = node.create_publisher(Twist, "/cmd_vel", 10)
    counts = {"left": None, "right": None}

    def on_counts(message):
        match = COUNTS_RE.search(message.data)
        if match:
            counts["left"] = int(match.group(1))
            counts["right"] = int(match.group(2))

    node.create_subscription(String, "/encoder_counts", on_counts, 10)
    command = Twist()
    command.linear.x = args.speed
    stop = Twist()
    reason = "timeout"

    try:
        discovery_deadline = time.monotonic() + 4.0
        while time.monotonic() < discovery_deadline:
            rclpy.spin_once(node, timeout_sec=0.05)
            if publisher.get_subscription_count() and counts["left"] is not None:
                break
        if publisher.get_subscription_count() == 0 or counts["left"] is None:
            raise RuntimeError("ROS command/count endpoints not discovered")

        deadline = time.monotonic() + args.timeout
        next_publish = time.monotonic()
        while time.monotonic() < deadline:
            left = counts["left"] or 0
            right = counts["right"] or 0
            mean = (left + right) / 2.0
            if (mean >= args.target_pulses and
                    left >= args.min_wheel_pulses and
                    right >= args.min_wheel_pulses):
                reason = "target"
                break
            publisher.publish(command)
            rclpy.spin_once(node, timeout_sec=0.02)
            next_publish += 0.05
            time.sleep(max(0.0, next_publish - time.monotonic()))
    finally:
        for _ in range(12):
            publisher.publish(stop)
            rclpy.spin_once(node, timeout_sec=0.01)
            time.sleep(0.04)
        print(
            f"RESULT reason={reason} HL={counts['left']} HR={counts['right']}",
            flush=True,
        )
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
