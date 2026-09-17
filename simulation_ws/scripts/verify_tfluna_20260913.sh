#!/usr/bin/env bash
set -euo pipefail
trap 'systemctl --user start robot-follower.service' EXIT
systemctl --user stop robot-follower.service
timeout --signal=INT --kill-after=3 60 avrdude -p atmega2560 -c wiring -P /dev/serial/by-id/usb-Arduino_Srl_Arduino_Mega_85438333036351A040D0-if00 -b115200 -D -U flash:v:/tmp/tfluna_20260913.hex:i
