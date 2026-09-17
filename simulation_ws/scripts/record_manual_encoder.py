"""Read-only manual wheel capture. No motor commands or counter resets."""
import json
import time
import urllib.request
from pathlib import Path

folder = Path(__file__).resolve().parents[1] / 'results' / 'manual_encoder'
folder.mkdir(parents=True, exist_ok=True)
path = folder / (time.strftime('%Y%m%d_%H%M%S') + '.json')
rows = []
start = time.monotonic()
try:
    while time.monotonic() - start < 180:
        with urllib.request.urlopen('http://192.168.40.74:8080/api/state', timeout=3) as response:
            state = json.load(response)
        motor = state['motor_status']
        if state['ages']['encoder_counts'] > 1 or state['ages']['motor_status'] > 1:
            raise RuntimeError('Stale telemetry; invalidate capture')
        if motor['Lpwm'] != 0 or motor['Rpwm'] != 0:
            raise RuntimeError('Powered movement detected; invalidate manual capture')
        rows.append(dict(t=time.monotonic()-start, encoders=state['encoder_counts'],
                         motor=motor, ages=state['ages']))
        if len(rows) == 1:
            path.write_text(json.dumps(rows), encoding='utf-8')
            print('READY baseline=' + state['encoder_counts'] + ' file=' + str(path), flush=True)
        if len(rows) % 10 == 0:
            path.write_text(json.dumps(rows), encoding='utf-8')
        time.sleep(.2)
finally:
    path.write_text(json.dumps(rows), encoding='utf-8')
    print('SAVED ' + str(path), flush=True)
