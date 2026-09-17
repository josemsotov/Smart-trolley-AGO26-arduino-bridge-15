#!/usr/bin/env bash
set -euo pipefail
cleanup() {
  systemctl --user stop smooth-bench-bridge.service || true
  systemctl --user start robot-follower.service || true
}
trap cleanup EXIT
systemctl --user stop robot-follower.service
systemd-run --user --collect --unit=smooth-bench-bridge --property=RuntimeMaxSec=90 --property=KillSignal=SIGINT /bin/bash /tmp/ros_zenoh_test_env.sh ros2 run arduino_bridge_ros2 arduino_node --ros-args -r /cmd_vel:=/cmd_vel/web -p cmd_timeout:=0.35
sleep 9
timeout --signal=INT --kill-after=3 60 python3 /tmp/left_normal_20260911.py "$@"
