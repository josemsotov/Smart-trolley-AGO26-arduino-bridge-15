# Obstacle stop prototype - not active

Reviewed mux: selects commands without obstacle input. Existing cmd_vel_guard
is monitor-only. New obstacle_gate_core.py is isolated decision logic, NOT
wired to /cmd_vel. Ten local unit tests pass (front, depth, rear, retreat,
rotation, stale sensors, zero, nonfinite commands, unknown space, clear).
Tests are synthetic booleans, not a physical collision avoidance validation.

Passive ROS probe on Pi, two 12s captures: 121 scans each (~10Hz), 431/456
then423/454 valid rays, nearest range0.406m in scan frame (not front clearance).
Depth received0 messages with best-effort and reliable subscriptions. Web depth
age subsequently98.45s; initially0.616s, so stream stopped during this work.
Kinect USB camera/audio/motor still enumerate. Root cause not established.
No motor commands, firmware changes, service restarts or persistent deployment
were performed in this stage. Motor telemetry remains PWM/RPM0.

Before activation: recover depth stream; confirm sensor extrinsics/tilt and
robot footprint; convert observations to directional footprint clearances;
validate invalid-depth/scan coverage and stopping margins; test actual objects
without motion, then integrate after mux before bridge with stale-data stop.
LiDAR configured at z1.35m: cannot assume low-obstacle or cliff coverage.
Retreat only if rear space is known clear; turns need swept-footprint clearance.
