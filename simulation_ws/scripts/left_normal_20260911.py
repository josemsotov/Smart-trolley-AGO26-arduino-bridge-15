"""Left-only suspended test through normal v handler, not q diagnostic."""
import json, re, time, argparse
from pathlib import Path
from bench_smooth_20260910 import request

parser=argparse.ArgumentParser()
parser.add_argument('--edge-test',action='store_true')
parser.add_argument('--scale',type=int,default=100)
args=parser.parse_args()
rows=[]
edge_snapshots=[]
out=Path('/home/josemsotov/robot_calibration')/('left_normal_'+time.strftime('%Y%m%d_%H%M%S')+'.json')
def sample():
    s=request('/api/state'); m=s['motor_status']
    if s['ages']['motor_status'] is None or s['ages']['motor_status']>1:
        raise RuntimeError('Stale motor telemetry')
    if s['ages']['encoder_counts'] is None or s['ages']['encoder_counts']>1:
        raise RuntimeError('Stale counts')
    if m['Rpwm']!=0 or max(abs(m['Lrpm']),abs(m['Rrpm']))>120:
        raise RuntimeError('Unexpected right PWM or excessive RPM')
    if s['stadia_state'].get('stadia')=='connected':
        raise RuntimeError('Unexpected manual controller')
    return s
try:
    deadline=time.monotonic()+15
    while True:
        request('/api/cmd_vel',{'linear':0,'angular':0});time.sleep(.2)
        s=request('/api/state')
        if s['ages']['motor_status'] is not None and s['ages']['motor_status']<.5:break
        if time.monotonic()>deadline:raise RuntimeError('No zero handshake')
    assert s['motor_status']['Lpwm']==s['motor_status']['Rpwm']==0
    # Reapply the documented bench profile following the serial-open reset.
    for cmd in ['hc off','k off','hb off','k smooth','k floor 18']:
        request('/api/raw_command',{'command':cmd});time.sleep(.1)
    s=request('/api/state')
    assert any('k smooth=1' in x for x in s['raw_rx'])
    assert any('k floor=18' in x for x in s['raw_rx'])
    request('/api/raw_command',{'command':'j leftscale '+str(args.scale)})
    time.sleep(.2)
    assert any('j leftscale='+str(args.scale) in x for x in request('/api/state')['raw_rx'])
    for trial,demand in enumerate([15,15] if args.edge_test else [15,20,25]):
        request('/api/cmd_vel',{'linear':0,'angular':0})
        time.sleep(.15)
        sample()
        request('/api/raw_command',{'command':'j stat'})
        time.sleep(.2)
        before=sample()
        edge_snapshots.append(dict(trial=trial,phase='before',encoders=before['encoder_counts'],stats=[x for x in before['raw_rx'] if x.startswith('j STAT')][-1:]))
        print('START demand',demand,flush=True)
        start=time.monotonic()
        next_stat=0
        while time.monotonic()-start<11:
            t=time.monotonic()-start
            factor=min(1,t/2) if t<8 else 0
            wheel_v=demand/120*factor
            request('/api/cmd_vel',{'linear':wheel_v/2,'angular':wheel_v/.82})
            if args.edge_test and t>=next_stat:
                request('/api/raw_command',{'command':'j stat'})
                next_stat=t+.5
            s=sample()
            rows.append(dict(trial=trial,demand=demand,t=t,motor=s['motor_status'],encoders=s['encoder_counts'],ages=s['ages'],stats=[x for x in s['raw_rx'] if x.startswith('j STAT')][-1:]))
            time.sleep(.1)
        request('/api/raw_command',{'command':'j stat'})
        time.sleep(.15)
        after=sample()
        edge_snapshots.append(dict(trial=trial,phase='after',encoders=after['encoder_counts'],stats=[x for x in after['raw_rx'] if x.startswith('j STAT')][-1:]))
        print('END',demand,s['encoder_counts'],flush=True)
    summary={}
    for trial in sorted(set(r['trial'] for r in rows)):
        hold=[r for r in rows if r['trial']==trial and 3<=r['t']<=7.8]
        def counts(r):return {k:int(v) for k,v in re.findall(r'\b(OL|OR|HL|HR)=(\d+)',r['encoders'])}
        first,last=counts(hold[0]),counts(hold[-1])
        delta={k:last[k]-first[k] for k in first}
        summary[trial]=dict(filter_scale_pct=args.scale,demand=hold[0]['demand'],seconds=hold[-1]['t']-hold[0]['t'],counts=delta)
    print(json.dumps(summary),flush=True)
    print(json.dumps(edge_snapshots),flush=True)
    out.with_suffix('.summary.json').write_text(json.dumps(summary,indent=2))
finally:
    try:request('/api/cmd_vel',{'linear':0,'angular':0})
    finally:
        out.parent.mkdir(exist_ok=True)
        out.write_text(json.dumps(rows))
        out.with_suffix('.edges.json').write_text(json.dumps(edge_snapshots,indent=2))
        print('SAVED',out,flush=True)
