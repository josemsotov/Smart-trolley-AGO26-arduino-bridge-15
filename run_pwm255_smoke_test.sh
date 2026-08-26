#!/usr/bin/env bash
set -euo pipefail
base=http://127.0.0.1:8080

raw() {
  curl --fail --silent --show-error --json "{\"command\":\"$1\"}" \
    "$base/api/raw_command" >/dev/null
}

cleanup() {
  raw STOP || true
  raw INHABILITAR || true
}
trap cleanup EXIT INT TERM

for pwm in 10 20 40; do
  for side in L R; do
    echo "TEST side=$side pwm=$pwm"
    raw "q $side $pwm"
    sleep 1.4
  done
done

cleanup
sleep 0.5
curl --fail --silent --show-error "$base/api/state" | python3 -c '
import json, sys
state = json.load(sys.stdin)
for line in state.get("raw_rx", []):
    if line.startswith("q "):
        print(line)
print("ENCODERS", state.get("encoder_counts"))
'
trap - EXIT INT TERM
