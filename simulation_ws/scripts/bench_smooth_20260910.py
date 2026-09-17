"""Bounded manual-bench characterization through the normal web/mux watchdog."""
import argparse, json, math, statistics, time, urllib.request
from pathlib import Path

def request(route, payload=None):
    data=None if payload is None else json.dumps(payload).encode()
    req=urllib.request.Request('http://127.0.0.1:8080'+route,data=data,
                               headers={'Content-Type':'application/json'})
    return json.load(urllib.request.urlopen(req, timeout=1.0))

def main():
    p=argparse.ArgumentParser(); p.add_argument('--tag',required=True)
    p.add_argument('--pi',default='off'); p.add_argument('--isolated',action='store_true')
    p.add_argument('--profile',choices=['legacy','smooth'],default='legacy')
    p.add_argument('--floor',type=int,default=18); a=p.parse_args()
    rows=[]; out=Path('/home/josemsotov/robot_calibration')/(a.tag+'.json')
    out.parent.mkdir(exist_ok=True)
    try:
        deadline=time.monotonic()+15
        while True:
            request('/api/cmd_vel',{'linear':0,'angular':0})
            time.sleep(.2)
            s=request('/api/state')
            age=s['ages'].get('motor_status')
            if age is not None and age<.5:
                break
            if time.monotonic()>deadline:
                raise RuntimeError('No fresh telemetry after zero-command handshake')
        assert s['motor_status']['Lpwm']==s['motor_status']['Rpwm']==0
        for cmd in ('hc off','k off','hb off'):
            request('/api/raw_command',{'command':cmd})
        request('/api/raw_command',{'command':'k '+a.profile})
        time.sleep(.3)
        expected='k smooth='+str(int(a.profile=='smooth'))
        if not any(expected in line for line in request('/api/state')['raw_rx']):
            raise RuntimeError('Firmware profile acknowledgement missing: '+expected)
        request('/api/raw_command',{'command':'k floor '+str(a.floor)})
        if a.pi!='off':
            request('/api/raw_command',{'command':'k '+a.pi+' 0.0'})
            request('/api/raw_command',{'command':'k on'})
        request('/api/mode',{'mode':'STADIA'}); time.sleep(1)
        for label,v,w in [('forward_low',.08,0),('forward',.22,0),('reverse',-.22,0),('pivot',0,.40)]:
            print('START',label,flush=True)
            start=time.monotonic(); due=start
            while time.monotonic()-start<7:
                t=time.monotonic()-start
                factor=min(1,t/1.5) if t<5.5 else 0
                request('/api/cmd_vel',{'linear':v*factor,'angular':w*factor})
                s=request('/api/state'); m=s['motor_status']
                if s['ages']['motor_status'] is None or s['ages']['motor_status']>1.5:
                    raise RuntimeError('Stale motor telemetry')
                if max(abs(m.get('Lrpm',0)),abs(m.get('Rrpm',0)))>150:
                    raise RuntimeError('Bench RPM limit')
                if not a.isolated and s['field_state'].get('effective_mode')!='STADIA':
                    raise RuntimeError('Manual mode lost')
                rows.append(dict(segment=label,t=t,command=[v*factor,w*factor],
                                 motor=m,encoders=s['encoder_counts'],age=s['ages']['motor_status']))
                due+=.1;time.sleep(max(0,due-time.monotonic()))
            print('END',label,flush=True)
    finally:
        for route,payload in [('/api/cmd_vel',{'linear':0,'angular':0}),
            ('/api/mode',{'mode':'IDLE'}),('/api/raw_command',{'command':'k off'}),
            ('/api/raw_command',{'command':'hc off'})]:
            try:request(route,payload)
            except Exception:pass
        out.write_text(json.dumps(rows))
    summary={}
    for label in sorted(set(r['segment'] for r in rows)):
        subset=[r['motor'] for r in rows if r['segment']==label and 2.5<r['t']<5.5]
        summary[label]={}
        for wheel in ('L','R'):
            rpm=[x.get(wheel+'rpm',0) for x in subset]
            pwm=[x.get(wheel+'pwm',0) for x in subset]
            summary[label][wheel]=dict(rpm_mean=round(statistics.mean(rpm),2),
                rpm_std=round(statistics.pstdev(rpm),2), pwm_mean=round(statistics.mean(pwm),2),
                pwm_zero_fraction=round(sum(v==0 for v in pwm)/len(pwm),2),samples=len(rpm))
    print(json.dumps(summary,indent=2),flush=True)
    out.with_suffix('.summary.json').write_text(json.dumps(summary,indent=2))

if __name__=='__main__':main()
