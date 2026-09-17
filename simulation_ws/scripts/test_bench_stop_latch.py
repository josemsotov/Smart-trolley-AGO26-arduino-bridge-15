import unittest
from bench_stop_latch import advance_latch

class LatchTests(unittest.TestCase):
    def test_clear(self):self.assertIsNone(advance_latch(None,None,1))
    def test_obstacle(self):self.assertEqual(advance_latch(None,'obstacle',1),'obstacle')
    def test_removed(self):self.assertEqual(advance_latch('obstacle',None,2),'obstacle')
    def test_timeout(self):self.assertEqual(advance_latch(None,None,20),'time_limit')
    def test_loss(self):self.assertEqual(advance_latch(None,'stale_sensor_or_motor',2),'stale_sensor_or_motor')
    def test_stop_priority(self):self.assertEqual(advance_latch('operator_request','obstacle',30),'operator_request')
if __name__=='__main__':unittest.main()
