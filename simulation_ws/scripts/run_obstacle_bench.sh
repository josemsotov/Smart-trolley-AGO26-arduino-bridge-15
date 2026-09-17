#!/usr/bin/env bash
set -euo pipefail
# Temporarily stop arbiter and gesture-command node; retain camera/depth.
cleanup() {
  systemctl --user restart robot-follower.service
}
trap cleanup EXIT
mapfile -t mux_pids < <(pgrep -f '^/usr/bin/python3 /home/josemsotov/robot_ws/install/lib/robot_follower/cmd_vel_mux ')
if [ "${#mux_pids[@]}" -ne 1 ]; then echo 'Expected exactly one mux'; exit 1; fi
mapfile -t gesture_pids < <(pgrep -f '^/usr/bin/python3 /home/josemsotov/robot_ws/install/lib/robot_follower/open_palm_node ')
if [ "${#gesture_pids[@]}" -ne 1 ]; then echo 'Expected exactly one gesture node'; exit 1; fi
kill -INT "${gesture_pids[0]}"
kill -INT "${mux_pids[0]}"
sleep 2
if pgrep -f '^/usr/bin/python3 /home/josemsotov/robot_ws/install/lib/robot_follower/open_palm_node ' >/dev/null; then echo 'Gesture node still running'; exit 1; fi
timeout --signal=INT --kill-after=3 65 /bin/bash /tmp/ros_zenoh_test_env.sh python3 /tmp/bench_obstacle_stop.py --armed
