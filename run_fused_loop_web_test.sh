#!/usr/bin/env bash
set -u
base=http://127.0.0.1:8080
cleaned=0
raw() {
  curl --fail --silent --show-error --json "{\"command\":\"$1\"}" "$base/api/raw_command" >/dev/null
}
cleanup() {
  if [ "$cleaned" -eq 1 ]; then return; fi
  cleaned=1
  raw 'v 0.000 0.000' || true
  raw 'STOP' || true
  raw 'k off' || true
  curl --fail --silent --show-error --json '{"linear":0.0,"angular":0.0}' \
    "$base/api/cmd_vel" >/dev/null || true
  systemctl --user restart robot-follower.service || true
}
trap cleanup EXIT INT TERM

raw 'n selftest'
raw 'r'
raw 'k 0.15 0.0'
raw 'k on'
raw 'HABILITAR'
mux_pid=$(pgrep -f '/install/lib/robot_follower/cmd_vel_mux --ros-args' | head -n 1)
if [ -z "$mux_pid" ]; then
  echo 'cmd_vel_mux PID not found' >&2
  exit 2
fi
kill -TERM "$mux_pid"
sleep 1
for _ in $(seq 1 60); do
  raw 'v 0.300 0.000'
  sleep 0.1
done
cleanup
sleep 7
curl --fail --silent --show-error "$base/api/state" | python3 -c '
import json,sys
s=json.load(sys.stdin)
print("MOTOR_STATUS", s.get("motor_status"))
for line in s.get("raw_rx", []):
    if "SELFTEST" in line or "Lfrpm=" in line:
        print(line)
'
trap - EXIT INT TERM
