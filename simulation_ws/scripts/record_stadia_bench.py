"""Passive Stadia capture: never sends motion commands."""
import json
import argparse
import time
import urllib.request
from pathlib import Path

parser = argparse.ArgumentParser()
parser.add_argument('--duration', type=float, default=60)
args = parser.parse_args()
out = Path(__file__).resolve().parents[1] / 'results' / 'smooth_20260910'
out.mkdir(parents=True, exist_ok=True)
dest = out / ('stadia_' + time.strftime('%Y%m%d_%H%M%S') + '.json')
rows = []
start = time.monotonic()
print('RECORDING ' + str(dest), flush=True)
try:
    while time.monotonic() - start < args.duration:
        t = time.monotonic() - start
        try:
            with urllib.request.urlopen('http://192.168.40.74:8080/api/state', timeout=2) as response:
                s = json.load(response)
            rows.append(dict(t=t, motor=s.get('motor_status'),
                encoders=s.get('encoder_counts'), ages=s.get('ages'),
                stadia=s.get('stadia_state'), command=s.get('cmd_vel')))
        except Exception as exc:
            rows.append(dict(t=t, error=str(exc)))
        time.sleep(.1)
finally:
    dest.write_text(json.dumps(rows), encoding='utf-8')
    print('SAVED ' + str(dest) + ' samples=' + str(len(rows)), flush=True)
