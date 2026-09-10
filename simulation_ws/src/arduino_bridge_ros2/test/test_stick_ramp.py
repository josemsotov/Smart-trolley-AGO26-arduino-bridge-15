import unittest
from arduino_bridge_ros2.stick_ramp import ramp


class RampTest(unittest.TestCase):
    def test_acceleration_bound_and_full_authority(self):
        v = 0.0
        for _ in range(50):
            nxt = ramp(v, .4, .05, .2, .5)
            self.assertLessEqual(nxt-v, .01000001)
            v = nxt
        self.assertAlmostEqual(v, .4)

    def test_reversal_stops_before_crossing(self):
        self.assertAlmostEqual(ramp(.01, -.4, .05, .2, .5), 0)
        self.assertAlmostEqual(ramp(0, -.4, .05, .2, .5), -.01)

    def test_release_and_stalled_timer(self):
        self.assertEqual(ramp(.4, 0, .05, .2, .5), 0)
        self.assertAlmostEqual(ramp(0, .4, 5, .2, .5), .02)
        self.assertEqual(ramp(0, float('nan'), .05, .2, .5), 0)

if __name__ == '__main__':
    unittest.main()
