#!/usr/bin/env bash
set -euo pipefail

MODE="${1:-mapping}"
MAP_FILE="${2:-}"

case "$MODE" in
  mapping|indoor|outdoor) ;;
  *) echo "Uso: $0 {mapping|indoor|outdoor} [pose_graph]" >&2; exit 2 ;;
esac
if [[ "$MODE" == indoor && -z "$MAP_FILE" ]]; then
  echo "El modo indoor requiere el path del pose-graph." >&2
  exit 2
fi

set +u
source /opt/ros/jazzy/setup.bash
source /home/josemsotov/robot_ws/install/setup.bash
set -u

export RMW_IMPLEMENTATION=rmw_zenoh_cpp
export ZENOH_ROUTER_CHECK_ATTEMPTS=0
export AMENT_PREFIX_PATH="/home/josemsotov/ros_zenoh_overlay/root/opt/ros/jazzy:${AMENT_PREFIX_PATH}"
export LD_LIBRARY_PATH="/home/josemsotov/ros_zenoh_overlay/root/opt/ros/jazzy/lib:/home/josemsotov/ros_zenoh_overlay/root/opt/ros/jazzy/opt/zenoh_cpp_vendor/lib:${LD_LIBRARY_PATH:-}"

args=(mode:="$MODE")
if [[ -n "$MAP_FILE" ]]; then
  args+=(map_file:="$MAP_FILE")
fi
exec ros2 launch robot_follower hybrid_navigation.launch.py "${args[@]}"
