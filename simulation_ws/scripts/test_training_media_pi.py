"""HTTP smoke checks: synthetic upload, rejected invalid input, Kinect clip."""
import json
import subprocess
import tempfile
import time
import urllib.request
import urllib.error
from pathlib import Path

BASE='http://127.0.0.1:8080'
def get(route):
    return json.load(urllib.request.urlopen(BASE+route, timeout=15))
def post(route, data, headers=None):
    return json.load(urllib.request.urlopen(urllib.request.Request(BASE+route, data=data,
        headers=headers or {'Content-Type':'application/json'}),timeout=120))
with tempfile.TemporaryDirectory() as folder:
    path=Path(folder)/'synthetic.mp4'
    subprocess.run(['ffmpeg','-v','error','-f','lavfi','-i','color=c=green:s=320x240:r=120',
        '-t','1','-c:v','libx264','-threads','1','-pix_fmt','yuv420p',str(path)],check=True)
    result=post('/api/training/upload',path.read_bytes(),{'X-Filename':'test.mp4'})
    assert result['fps']==120 and result['width']==320, result
    assert any(v['file']==result['file'] for v in get('/api/training/videos'))
    print('Synthetic phone upload/list OK:',result)
    try:
        post('/api/training/upload',b'not a video',{'X-Filename':'invalid.mp4'})
        raise AssertionError('Invalid video accepted')
    except urllib.error.HTTPError as e:
        assert e.code==422, e.code
    print('Invalid video rejection OK')
    post('/api/camera/video',b'{"action":"start"}')
    time.sleep(4)
    clip=post('/api/camera/video',b'{"action":"stop"}')
    print('Kinect recording:',clip)
    assert clip['frames']>0 and clip['fps']>0
    print('Camera telemetry:',get('/api/state')['camera'])
