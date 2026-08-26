#!/usr/bin/env bash
set -u
base=http://127.0.0.1:8080
curl --fail --silent --show-error --json '{"command":"z"}' \
  "$base/api/raw_command" >/dev/null
sleep 0.5
curl --fail --silent --show-error "$base/api/state" | python3 -c '
import json,sys
for line in json.load(sys.stdin).get("raw_rx", []):
    if line.startswith("z "):
        print(line)
'
