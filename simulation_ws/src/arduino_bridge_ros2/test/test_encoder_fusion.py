from arduino_bridge_ros2.encoder_fusion import WheelEncoderFusion


def feed(fusion, opto, hall, count=10):
    result = None
    for _ in range(count):
        result = fusion.update(opto, hall, moving=True)
    return result


def test_consistent_opto_is_diagnostic_but_hall_drives_delta():
    result = feed(WheelEncoderFusion(), 4, 3)
    assert result['source'] == 'HALL_PRIMARY'
    assert result['delta'] == 4
    assert result['confidence'] == 0.85


def test_moderate_disagreement_still_uses_hall():
    result = feed(WheelEncoderFusion(), 4.4, 3)
    assert result['source'] == 'HALL_PRIMARY'
    assert result['delta'] == 4


def test_noisy_opto_is_rejected_without_changing_distance():
    result = feed(WheelEncoderFusion(), 20, 3)
    assert result['source'] == 'HALL_PRIMARY_OPTO_WARN'
    assert result['delta'] == 4
    assert result['error'] > 1.0


def test_opto_only_motion_is_never_integrated():
    result = feed(WheelEncoderFusion(), 20, 0)
    assert result['source'] == 'HALL_WAIT'
    assert result['delta'] == 0


def test_stopped_wheel_rejects_counts_and_resets_window():
    fusion = WheelEncoderFusion()
    feed(fusion, 4, 3)
    result = fusion.update(9, 9, moving=False)
    assert result['source'] == 'STOP'
    assert result['delta'] == 0