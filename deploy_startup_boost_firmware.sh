#!/usr/bin/env bash
set -euo pipefail

service=robot-follower.service
port=/dev/ttyACM0
new_hex=/tmp/smart_trolley_ff120_v5.hex
backup_dir=/home/josemsotov/robot_backups
backup_hex="$backup_dir/pre_ff120_v5_20260828.hex"

restart_service() {
  systemctl --user start "$service" || true
}
trap restart_service EXIT

mkdir -p "$backup_dir"
systemctl --user stop "$service"
avrdude -p atmega2560 -c wiring -P "$port" -b 115200 \
  -U "flash:r:$backup_hex:i"
avrdude -p atmega2560 -c wiring -P "$port" -b 115200 -D \
  -U "flash:w:$new_hex:i"
restart_service
trap - EXIT
systemctl --user is-active "$service"
echo "BACKUP=$backup_hex"
