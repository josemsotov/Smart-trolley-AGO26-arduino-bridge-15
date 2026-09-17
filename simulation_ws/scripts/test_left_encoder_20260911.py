"""Bounded firmware q diagnostic; fixed 2500us opto filter, NOT drive profile."""
import json
import time
import urllib.request
from pathlib import Path

def api(route, payload=None):
    data = None if payload is None else json.dumps(payload).encode()
    req = urllib.request.Request('http://192.168.40.74:8080/api/'+route,
        data=data, headers={'Content-Type':'application/json'})
    with urllib.request.urlopen(req, timeout=3) as response:
        return json.load(response)

def stopped():
    s = api('state')
    assert s['ages']['motor_status'] < 1
    assert s['motor_status']['Lpwm'] == s['motor_status']['Rpwm'] == 0
    assert s['stadia_state']['stadia'] == 'disconnected'
    assert s['field_state']['effective_mode'] in ('PAUSE', 'IDLE')
    return s

path = Path(__file__).resolve().parents[1]/'results'/'manual_encoder'/('left_powered_'+time.strftime('%Y%m%d_%H%M%S')+'.json')
path.parent.mkdir(parents=True, exist_ok=True)
records = []
try:
    for pwm in (15, 20, 25):
        before = stopped()
        expected = 'q OK side=L pwm='+str(pwm)+' '
        assert not any(expected in x for x in before['raw_rx']), 'Old acknowledgement present'
        print('START PWM', pwm, flush=True)
        api('raw_command', {'command':'q L '+str(pwm)})
        deadline = time.monotonic()+5
        result = None
        while time.monotonic() < deadline:
            time.sleep(.15)
            s = api('state')
            matches = [x for x in s['raw_rx'] if expected in x]
            if matches:
                result = matches[-1]
                break
        if result is None:
            raise RuntimeError('No diagnostic acknowledgement')
        print(result, flush=True)
        time.sleep(3)
        after = stopped()
        records.append(dict(pwm=pwm,result=result,before=before['encoder_counts'],
            after=after['encoder_counts'],motor=after['motor_status'],filter_us=2500))
        path.write_text(json.dumps(records,indent=2),encoding='utf-8')
        if ' R=0 ' not in result or ' OR=0' not in result:
            raise RuntimeError('Unexpected right-wheel counts')
finally:
    api('cmd_vel', {'linear':0,'angular':0})
    path.write_text(json.dumps(records,indent=2),encoding='utf-8')
    print('SAVED',path,flush=True)
