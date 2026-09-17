"""Summarize recorded bench samples without treating filtered RPM as ground truth."""
import json
import re
import statistics
import sys
from pathlib import Path

for name in sys.argv[1:]:
    rows = json.loads(Path(name).read_text())
    result = {}
    for segment in sorted({r['segment'] for r in rows}):
        hold = [r for r in rows if r['segment'] == segment and 2.5 < r['t'] < 5.5]
        if len(hold) < 2:
            continue
        counts = [dict((k, int(v)) for k, v in re.findall(r'\b(OL|OR|HL|HR)=(\d+)', r['encoders'])) for r in hold]
        elapsed = hold[-1]['t'] - hold[0]['t']
        result[segment] = {}
        for wheel in 'LR':
            hall = counts[-1]['H'+wheel] - counts[0]['H'+wheel]
            opto = counts[-1]['O'+wheel] - counts[0]['O'+wheel]
            rpm = [r['motor'].get(wheel+'rpm', 0) for r in hold]
            result[segment][wheel] = dict(hall=hall, opto=opto,
                count_rpm=round(hall * 60 / (45 * elapsed), 2),
                reported_rpm_std=round(statistics.pstdev(rpm), 2),
                zero_pwm_fraction=round(sum(r['motor'][wheel+'pwm'] == 0 for r in hold)/len(hold), 2))
    print(Path(name).name, json.dumps(result, indent=2))
