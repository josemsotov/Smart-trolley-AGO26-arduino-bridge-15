import unittest
from robot_follower.obstacle_gate_core import decide

class GateTests(unittest.TestCase):
    def decision(self,v=.1,w=0,**overrides):
        inputs=dict(lidar_fresh=True,depth_fresh=True,front_clear=True,
                    rear_clear=True,rotation_clear=True,depth_front_clear=True)
        inputs.update(overrides)
        return decide(v,w,**inputs)
    def test_front(self):
        self.assertEqual(self.decision(front_clear=False)['linear'],0)
    def test_depth(self):
        self.assertEqual(self.decision(depth_front_clear=False)['linear'],0)
    def test_retreat(self):
        self.assertEqual(self.decision(v=-.1,front_clear=False,depth_front_clear=False)['linear'],-.1)
    def test_rear_unknown(self):
        self.assertEqual(self.decision(v=-.1,rear_clear=None)['linear'],0)
    def test_turn(self):
        r=self.decision(w=.2,rotation_clear=False)
        self.assertEqual((r['linear'],r['angular']),(0,0))
    def test_sensor_loss(self):
        for key in ['lidar_fresh','depth_fresh']:
            self.assertEqual(self.decision(**{key:False})['linear'],0)
    def test_stop(self):
        self.assertEqual(self.decision(v=0,depth_fresh=False)['reason'],'stop')
    def test_nan(self):
        self.assertEqual(self.decision(v=float('nan'))['reason'],'invalid_command')
    def test_unknown_front(self):
        self.assertEqual(self.decision(front_clear=None)['linear'],0)
    def test_clear(self):
        self.assertEqual(self.decision()['linear'],.1)

if __name__=='__main__':unittest.main()
