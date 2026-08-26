#!/usr/bin/env bash
set -euo pipefail
base=http://127.0.0.1:8080
raw() {
  curl --fail --silent --show-error --json "{\"command\":\"$1\"}" \
    "$base/api/raw_command" >/dev/null
}
latest() {
  curl --fail --silent --show-error "$base/api/state" | python3 -c '
import json,sys
lines=[x for x in json.load(sys.stdin).get("raw_rx",[]) if x.startswith("q ")]
print(lines[-1] if lines else "q NO_RESPONSE")
'
}
cleanup() { raw STOP || true; raw INHABILITAR || true; }
trap cleanup EXIT INT TERM
for pwm in 60 80 90; do
  for side in L R; do
    raw "q $side $pwm"
    sleep 1.4
    latest
  done
done
cleanup
trap - EXIT INT TERM
