#!/usr/bin/env bash
set -euo pipefail
port=/dev/serial/by-id/usb-Arduino_Srl_Arduino_Mega_85438333036351A040D0-if00
backup=$(mktemp -d /home/josemsotov/robot_backups/smooth_20260910_XXXXXX)
trap 'systemctl --user start robot-follower.service' EXIT
systemctl --user stop robot-follower.service
avrdude -p atmega2560 -c wiring -P "$port" -b 115200 -U "flash:r:$backup/original.hex:i"
if ! avrdude -p atmega2560 -c wiring -P "$port" -b 115200 -D -U flash:w:/tmp/smooth_bench.hex:i; then
  avrdude -p atmega2560 -c wiring -P "$port" -b 115200 -D -U "flash:w:$backup/original.hex:i"
  exit 1
fi
echo "BACKUP=$backup/original.hex"
