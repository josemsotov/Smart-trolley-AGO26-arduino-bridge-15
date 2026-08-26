#!/usr/bin/env bash
set -u
base=http://127.0.0.1:8080
raw() {
  curl --fail --silent --show-error --json "{\"command\":\"$1\"}" "$base/api/raw_command" >/dev/null
}
cleanup() {
  raw 'STOP' || true
  raw 'INHABILITAR' || true
}
trap cleanup EXIT INT TERM
raw 'r'
raw 'q L 30'
sleep 2
raw 'q R 30'
sleep 2
cleanup
sleep 1
curl --fail --silent --show-error "$base/api/state" | python3 -c '
import json,sys
s=json.load(sys.stdin)
print(s.get("encoder_counts"))
for line in s.get("raw_rx", []):
    if line.startswith("q "):
        print(line)
'
trap - EXIT INT TERM
