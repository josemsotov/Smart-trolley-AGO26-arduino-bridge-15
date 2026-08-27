#!/usr/bin/env bash
set -euo pipefail

rz=/tmp/ros_zenoh_test_env.sh
publisher=/tmp/ros_hall_position_cmd.py
speed="${1:-0.10}"
target="${2:-5.3}"
timeout_s="${3:-3.0}"
mux_pid=""

raw() {
  curl --fail --silent --show-error --json "{\"command\":\"$1\"}" \
    http://127.0.0.1:8080/api/raw_command >/dev/null
}

cleanup() {
  raw 'k off' || true
  raw 'hc off' || true
  raw STOP || true
  raw INHABILITAR || true
  if [[ -n "$mux_pid" ]]; then kill -CONT "$mux_pid" 2>/dev/null || true; fi
}
trap cleanup EXIT INT TERM

mux_pid="$(pgrep -f '/cmd_vel_mux([[:space:]]|$)' | head -n1 || true)"
[[ -n "$mux_pid" ]] || { echo 'No se encontro cmd_vel_mux' >&2; exit 2; }
kill -STOP "$mux_pid"
raw r
raw 'k 0.75 0.0'
raw 'k on'
raw 'hc reset'
raw 'hc on'
"$rz" python3 "$publisher" --speed "$speed" --target-pulses "$target" \
  --min-wheel-pulses 4 --timeout "$timeout_s"
cleanup
trap - EXIT INT TERM
