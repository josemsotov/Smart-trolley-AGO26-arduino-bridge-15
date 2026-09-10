"""Command ramp; emergency stop bypasses this function."""
import math


def ramp(current, target, dt, acceleration, deceleration):
    if not all(math.isfinite(v) for v in (current, target, dt, acceleration, deceleration)):
        return 0.0
    if target == 0:
        return 0.0  # Releasing the stick must not prolong a motor command.
    dt = max(0.0, min(dt, 0.1))
    if current * target < 0:
        target = 0.0  # Brake to zero before accelerating in the other direction.
    rate = acceleration if abs(target) > abs(current) else deceleration
    step = max(0.0, rate) * dt
    return current + max(-step, min(step, target-current))
