#!/usr/bin/env bash
set -euo pipefail
port=/dev/serial/by-id/usb-Arduino_Srl_Arduino_Mega_85438333036351A040D0-if00
hex=/tmp/tfluna_20260913.hex
test -c "$port"
test -s "$hex"
backup=$(mktemp -d /home/josemsotov/robot_backups/pre_tfluna_20260913_XXXXXX)
trap 'systemctl --user start robot-follower.service' EXIT
systemctl --user stop robot-follower.service
timeout --signal=INT --kill-after=3 90 avrdude -p atmega2560 -c wiring -P "$port" -b115200 -U "flash:r:$backup/original.hex:i"
test -s "$backup/original.hex"
sha256sum "$backup/original.hex" "$hex"
if ! avrdude -p atmega2560 -c wiring -P "$port" -b115200 -D -U "flash:w:$hex:i"; then
  avrdude -p atmega2560 -c wiring -P "$port" -b115200 -D -U "flash:w:$backup/original.hex:i"
  exit 1
fi
echo "BACKUP=$backup/original.hex"
