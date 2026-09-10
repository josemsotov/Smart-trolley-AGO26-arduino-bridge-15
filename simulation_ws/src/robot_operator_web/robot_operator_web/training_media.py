"""Bounded video uploads; originals kept intact for later analysis."""
import asyncio
import json
import shutil
import subprocess
import uuid
from pathlib import Path

from fastapi import HTTPException, Request

LIMIT = 300 * 1024 * 1024


def probe(path):
    result = subprocess.run(['ffprobe', '-v', 'error', '-select_streams', 'v:0',
        '-show_entries', 'stream=width,height,avg_frame_rate:format=duration',
        '-of', 'json', str(path)], capture_output=True, timeout=15, check=True)
    data = json.loads(result.stdout)
    stream = data['streams'][0]
    n, d = stream['avg_frame_rate'].split('/')
    return dict(width=stream['width'], height=stream['height'],
                fps=float(n)/float(d) if float(d) else 0,
                duration=float(data['format'].get('duration', 0)))


def install_routes(app, media_dir):
    folder = Path(media_dir)
    upload_lock = asyncio.Lock()

    @app.post('/api/training/upload')
    async def upload(request: Request):
        suffix = Path(request.headers.get('x-filename', '')).suffix.lower()
        if suffix not in ('.mp4', '.mov', '.m4v', '.webm'):
            raise HTTPException(415, 'Usa MP4, MOV, M4V o WebM')
        if upload_lock.locked():
            raise HTTPException(409, 'Ya hay una carga en curso')
        async with upload_lock:
            if shutil.disk_usage(folder).free < LIMIT * 2:
                raise HTTPException(507, 'Espacio insuficiente en el Pi')
            name = 'phone_' + uuid.uuid4().hex + suffix
            path = folder / name
            total = 0
            try:
                with path.open('xb') as handle:
                    async with asyncio.timeout(180):
                        async for chunk in request.stream():
                            total += len(chunk)
                            if total > LIMIT:
                                raise HTTPException(413, 'Limite: 300 MB por video')
                            await asyncio.to_thread(handle.write, chunk)
                info = await asyncio.to_thread(probe, path)
                if info['duration'] <= 0 or not info['width'] or not info['height']:
                    raise ValueError('Invalid video')
                metadata = dict(file=name, url='/api/media/'+name, source='phone', **info)
                path.with_suffix(path.suffix+'.info.json').write_text(json.dumps(metadata))
                return metadata
            except BaseException as exc:
                path.unlink(missing_ok=True)  # Only this newly-created upload.
                if isinstance(exc, (HTTPException, asyncio.CancelledError)):
                    raise
                raise HTTPException(422, 'No se pudo leer el video o la carga excedio el tiempo limite') from None

    @app.get('/api/training/videos')
    async def videos():
        output=[]
        for path in sorted(folder.glob('*'), key=lambda p:p.stat().st_mtime, reverse=True):
            if path.suffix.lower() not in ('.mp4','.mov','.m4v','.webm','.avi'):
                continue
            if not path.name.startswith(('phone_', 'kinect_', 'video_')):
                continue
            info_path=path.with_suffix(path.suffix+'.info.json')
            info=json.loads(info_path.read_text()) if info_path.exists() else {}
            output.append(dict(info, file=path.name, url='/api/media/'+path.name))
            if len(output)>=50:
                break
        return output
