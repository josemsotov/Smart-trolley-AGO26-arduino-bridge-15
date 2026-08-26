#!/usr/bin/env bash
set -u
base=http://127.0.0.1:8080
raw() {
  curl --fail --silent --show-error --json "{\"command\":\"$1\"}" "$base/api/raw_command" >/dev/null
}
counts() {
  curl --fail --silent --show-error "$base/api/state" | python3 -c \
    'import json,sys; print(json.load(sys.stdin).get("encoder_counts"))'
}
q_lines() {
  curl --fail --silent --show-error "$base/api/state" | python3 -c '
import json,sys
for line in json.load(sys.stdin).get("raw_rx", []):
    if line.startswith("q "):
        print(line)
'
}
cleanup() {
  raw 'STOP' || true
  raw 'INHABILITAR' || true
}
trap cleanup EXIT INT TERM
raw 'r'
sleep 0.5
raw 'q L 30'
sleep 1.5
echo PWM30 "$(counts)"
q_lines
raw 'r'
sleep 0.5
raw 'q L 40'
sleep 1.5
echo PWM40 "$(counts)"
q_lines
cleanup
trap - EXIT INT TERM
