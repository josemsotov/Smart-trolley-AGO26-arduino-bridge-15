"""Fail-safe Hall/opto wheel odometry in a common 45-PPR domain."""
from collections import deque


class WheelEncoderFusion:
    """Blend agreeing sensors and fall back to Hall when opto is implausible."""

    def __init__(self, opto_ppr=45.0, hall_ppr=45.0, window_samples=10,
                 high_threshold=0.05, medium_threshold=0.12):
        self.ratio = float(opto_ppr) / float(hall_ppr)
        self.high_threshold = float(high_threshold)
        self.medium_threshold = float(medium_threshold)
        self._opto = deque(maxlen=int(window_samples))
        self._hall = deque(maxlen=int(window_samples))

    def reset(self):
        self._opto.clear()
        self._hall.clear()

    def update(self, opto_delta, hall_delta, moving=True):
        opto_delta = max(0.0, float(opto_delta))
        hall_delta = max(0.0, float(hall_delta))
        if not moving:
            self.reset()
            return {'delta': 0.0, 'source': 'STOP', 'confidence': 1.0,
                    'error': 0.0, 'opto_window': 0.0, 'hall_window': 0.0}

        self._opto.append(opto_delta)
        self._hall.append(hall_delta)
        opto_window = sum(self._opto)
        hall_window = sum(self._hall)

        # Never integrate opto-only motion while motor power is active. Bench
        # data showed motor EMI can create several times the physical count.
        if hall_window <= 0.0:
            return {'delta': 0.0, 'source': 'HALL_WAIT', 'confidence': 0.25,
                    'error': -1.0, 'opto_window': opto_window,
                    'hall_window': hall_window}

        hall_as_opto = hall_delta * self.ratio
        expected_window = hall_window * self.ratio
        error = abs(opto_window - expected_window) / expected_window
        if error <= self.high_threshold:
            delta = 0.5 * (opto_delta + hall_as_opto)
            source = 'HALL_OPTO_FUSED'
            confidence = 1.0
        elif error <= self.medium_threshold:
            # Prefer Hall near the warning boundary while still allowing the
            # second sensor to improve quantization and position resolution.
            delta = 0.25 * opto_delta + 0.75 * hall_as_opto
            source = 'HALL_OPTO_DEGRADED'
            confidence = 0.80
        else:
            delta = hall_as_opto
            source = 'HALL_PRIMARY_OPTO_WARN'
            confidence = 0.60
        return {'delta': delta, 'source': source,
                'confidence': confidence, 'error': error,
                'opto_window': opto_window, 'hall_window': hall_window}
