"""Conservative prototype decision logic. Not wired to motor output.

Clearance inputs must already be transformed to robot footprint coordinates.
No raw sensor range may be passed as footprint clearance without calibration.
"""
import math

def decide(linear, angular, *, lidar_fresh, depth_fresh, front_clear,
           rear_clear, rotation_clear, depth_front_clear):
    if not math.isfinite(linear) or not math.isfinite(angular):
        return dict(linear=0., angular=0., reason='invalid_command')
    if abs(linear)<1e-6 and abs(angular)<1e-6:
        return dict(linear=0., angular=0., reason='stop')
    reason=None
    if not lidar_fresh or not depth_fresh:
        reason='sensor_stale'
    elif linear>0 and (front_clear is not True or depth_front_clear is not True):
        reason='front_blocked_or_unknown'
    elif linear<0 and rear_clear is not True:
        reason='rear_blocked_or_unknown'
    elif abs(angular)>1e-6 and rotation_clear is not True:
        reason='rotation_blocked_or_unknown'
    return dict(linear=0. if reason else linear,
                angular=0. if reason else angular,
                reason=reason or 'candidate_clear')
