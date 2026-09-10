# Stadia ground validation candidate

Stadia now applies linear expo 1.6 and command acceleration limits of
0.20 m/s^2 and 0.45 rad/s^2. Deceleration limits for reversals are 0.50 m/s^2
and 1.0 rad/s^2. Neutral and emergency STOP command zero immediately.
Maximum requests remain 0.40 m/s and 0.70 rad/s; firmware FF120 unchanged.
Three offline ramp tests passed. Physical trajectory remains to be validated.

Arduino queried stationary: hc disabled, velocity PI disabled, IMU ready.
Enabled at runtime: `k 0.25 0.0`, `k on`, `hc on`.
Acknowledged k enabled=1, hc enabled=1, PWM/RPM 0/0 afterwards.
These runtime settings are lost at Arduino reset; intentionally not made
startup defaults before the ground comparison. Rollback: `hc off`, `k off`.

Next supervised checks: straight forward, straight reverse, left/right pivot.
Observe heading drift, wheel RPM mismatch and unwanted translation in pivot.
No commanded movement was generated during activation. Do not claim trajectory
accuracy or pivot-center stability based on static activation alone.
