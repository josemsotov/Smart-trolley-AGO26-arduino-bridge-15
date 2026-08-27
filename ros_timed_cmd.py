#!/usr/bin/env python3
"""Publish a velocity command for an exact interval after ROS initializes."""

import argparse
import time

import rclpy
from geometry_msgs.msg import Twist


def publish_zero(publisher, node, count=10):
    stop = Twist()
    for _ in range(count):
        publisher.publish(stop)
        rclpy.spin_once(node, timeout_sec=0.01)
        time.sleep(0.04)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--speed", type=float, required=True)
    parser.add_argument("--angular", type=float, default=0.0)
    parser.add_argument("--duration", type=float, required=True)
    parser.add_argument("--rate", type=float, default=20.0)
    args = parser.parse_args()
    if args.duration <= 0.0 or args.rate <= 0.0:
        parser.error("duration and rate must be positive")

    rclpy.init()
    node = rclpy.create_node("timed_cmd_vel_test")
    publisher = node.create_publisher(Twist, "/cmd_vel", 10)
    command = Twist()
    command.linear.x = args.speed
    command.angular.z = args.angular

    try:
        # Discovery completes before the measured motion interval begins.
        discovery_deadline = time.monotonic() + 3.0
        while time.monotonic() < discovery_deadline:
            rclpy.spin_once(node, timeout_sec=0.05)
            if publisher.get_subscription_count() > 0:
                break
        if publisher.get_subscription_count() == 0:
            raise RuntimeError("no /cmd_vel subscriber discovered")

        period = 1.0 / args.rate
        started = time.monotonic()
        deadline = started + args.duration
        next_publish = started
        while time.monotonic() < deadline:
            publisher.publish(command)
            rclpy.spin_once(node, timeout_sec=0.0)
            next_publish += period
            time.sleep(max(0.0, next_publish - time.monotonic()))
    finally:
        publish_zero(publisher, node)
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
