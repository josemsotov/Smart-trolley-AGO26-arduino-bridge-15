"""Exercise actual scan callback without needing a ROS installation."""
import ast
from collections import deque
import math
from pathlib import Path
from threading import Lock
from types import SimpleNamespace

source = Path(__file__).resolve().parents[1] / 'src/robot_operator_web/robot_operator_web/web_server.py'
tree = ast.parse(source.read_text(encoding='utf-8'))
cls = next(n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == 'OperatorNode')
method = next(n for n in cls.body if isinstance(n, ast.FunctionDef) and n.name == 'update_scan')
scope = {'math': math, 'LaserScan': object, 'now_s': lambda: 10.0}
exec(compile(ast.Module(body=[method], type_ignores=[]), str(source), 'exec'), scope)
state = SimpleNamespace(lock=Lock(), stamps={})
node = SimpleNamespace(state=state, scan_times={'scan': deque(), 'scan_lower': deque()})
msg = SimpleNamespace(ranges=[2., 3., float('inf'), 4., 1.], range_min=.02,
                      range_max=12., angle_min=0., angle_increment=math.pi/2,
                      header=SimpleNamespace(frame_id='sensor'))
scope['update_scan'](node, msg, 'scan')
scope['update_scan'](node, msg, 'scan_lower')
assert state.scan['front_min'] == 1.  # Includes 2*pi wraparound.
assert state.scan_lower['front_min'] == 1.
assert state.scan['valid_count'] == state.scan_lower['valid_count'] == 4
assert state.scan['points'][1][0] > 0 > state.scan_lower['points'][1][0]
assert state.scan is not state.scan_lower
assert set(state.stamps) == {'scan', 'scan_lower'}
print('PASS: independent states, inverted angles, wrapped front sector, invalid ranges')
