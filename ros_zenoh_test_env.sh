#!/usr/bin/env bash
set -euo pipefail

overlay=/home/josemsotov/ros_zenoh_overlay/root/opt/ros/jazzy
set +u
. /opt/ros/jazzy/setup.bash
. /home/josemsotov/robot_ws/install/setup.bash
set -u

export AMENT_PREFIX_PATH="$overlay:${AMENT_PREFIX_PATH:-}"
export LD_LIBRARY_PATH="$overlay/lib:$overlay/opt/zenoh_cpp_vendor/lib:${LD_LIBRARY_PATH:-}"
export RMW_IMPLEMENTATION=rmw_zenoh_cpp
export ROS_DOMAIN_ID=0
export ROS_AUTOMATIC_DISCOVERY_RANGE=LOCALHOST
export ZENOH_ROUTER_CHECK_ATTEMPTS=10
export ZENOH_CONFIG_OVERRIDE='connect/endpoints=["tcp/127.0.0.1:7447"]'

exec "$@"
