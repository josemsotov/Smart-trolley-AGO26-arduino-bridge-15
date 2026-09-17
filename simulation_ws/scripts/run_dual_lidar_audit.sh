#!/usr/bin/env bash
set -euo pipefail
set +u
source /opt/ros/jazzy/setup.bash
source /home/josemsotov/robot_ws/install/setup.bash
set -u
export RMW_IMPLEMENTATION=rmw_zenoh_cpp
export AMENT_PREFIX_PATH=/home/josemsotov/ros_zenoh_overlay/root/opt/ros/jazzy:${AMENT_PREFIX_PATH:-}
export LD_LIBRARY_PATH=/home/josemsotov/ros_zenoh_overlay/root/opt/ros/jazzy/lib:/home/josemsotov/ros_zenoh_overlay/root/opt/ros/jazzy/opt/zenoh_cpp_vendor/lib:/opt/ros/jazzy/opt/zenoh_cpp_vendor/lib:${LD_LIBRARY_PATH:-}
export ZENOH_ROUTER_CHECK_ATTEMPTS=0
python3 /home/josemsotov/robot_ws/scripts/audit_dual_lidar.py
