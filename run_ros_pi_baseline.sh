#!/usr/bin/env bash
set -euo pipefail

rz=/tmp/ros_zenoh_test_env.sh
timed_pub=/tmp/ros_timed_cmd.py
kp="${1:-0.25}"
speed="${2:-0.10}"
duration="${3:-2.0}"
heading="${4:-off}"
tag="${kp//./_}"
speed_tag="${speed//./_}"
log="/tmp/ros_pi_kp_${tag}_v_${speed_tag}_20260827.log"
mux_pid=""
echo_pids=()

raw() {
  curl --fail --silent --show-error --json "{\"command\":\"$1\"}" \
    http://127.0.0.1:8080/api/raw_command >/dev/null
}

zero() {
  timeout --kill-after=2 5 "$rz" ros2 topic pub --once /cmd_vel geometry_msgs/msg/Twist \
    '{linear: {x: 0.0}, angular: {z: 0.0}}' >/dev/null || true
}

cleanup() {
  zero
  raw 'k off' || true
  raw 'hc off' || true
  raw STOP || true
  raw INHABILITAR || true
  for pid in "${echo_pids[@]}"; do kill "$pid" 2>/dev/null || true; done
  if [[ -n "$mux_pid" ]]; then kill -CONT "$mux_pid" 2>/dev/null || true; fi
}
trap cleanup EXIT INT TERM

: >"$log"
mux_pid="$(pgrep -f '/cmd_vel_mux([[:space:]]|$)' | head -n1 || true)"
if [[ -z "$mux_pid" ]]; then
  echo 'No se encontro el proceso cmd_vel_mux' >&2
  exit 2
fi
kill -STOP "$mux_pid"

"$rz" ros2 topic echo /motor_status >>"$log" 2>&1 & echo_pids+=("$!")
"$rz" ros2 topic echo /encoder_fusion/status >>"$log" 2>&1 & echo_pids+=("$!")
"$rz" ros2 topic echo /encoder_counts >>"$log" 2>&1 & echo_pids+=("$!")
sleep 2

raw r
raw "k $kp 0.0"
raw 'k on'
if [[ "$heading" == "on" ]]; then
  raw 'hc reset'
  raw 'hc on'
else
  raw 'hc off'
fi
# The Python publisher starts its timer only after ROS initialization and
# discovery, avoiding loss of the whole motion interval during CLI startup.
"$rz" python3 "$timed_pub" --speed "$speed" --duration "$duration" --rate 20
zero
sleep 1

cleanup
trap - EXIT INT TERM
echo "LOG=$log"
