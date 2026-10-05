"""Bounded high-speed ELP capture with a browser-compatible review proxy."""
import asyncio
import json
import os
import shutil
import subprocess
import threading
import time
import uuid
from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse

from .training_media import probe


ELP_DEVICE = (
    "/dev/v4l/by-id/"
    "usb-Global_Shutter_Camera_Global_Shutter_Camera_01.00.00-video-index0"
)
CAPTURE_SECONDS = 15
MIN_FREE_BYTES = 700 * 1024 * 1024


class ElpRecorder:
    def __init__(self, media_dir: str, device: str = ELP_DEVICE) -> None:
        self.folder = Path(media_dir)
        self.device = device
        self.lock = threading.Lock()
        self.process: subprocess.Popen[bytes] | None = None
        self.worker: threading.Thread | None = None
        self.stop_requested = False
        self.phase = "idle"
        self.started_at: float | None = None
        self.master_path: Path | None = None
        self.proxy_path: Path | None = None
        self.last_error: str | None = None
        self.last_result: dict[str, Any] | None = None
        self.preview_process: subprocess.Popen[bytes] | None = None
        self.preview_worker: threading.Thread | None = None
        self.preview_stop = threading.Event()
        self.preview_jpeg: bytes | None = None
        self.preview_stamp: float | None = None
        self.preview_error: str | None = None

    def status(self) -> dict[str, Any]:
        with self.lock:
            elapsed = (
                min(CAPTURE_SECONDS, max(0.0, time.monotonic() - self.started_at))
                if self.started_at is not None and self.phase == "recording"
                else 0.0
            )
            size = (
                self.master_path.stat().st_size
                if self.master_path is not None and self.master_path.exists()
                else 0
            )
            return {
                "available": os.path.exists(self.device),
                "device": self.device,
                "profile": "1920x1080 MJPEG at 90 FPS",
                "max_duration": CAPTURE_SECONDS,
                "phase": self.phase,
                "recording": self.phase == "recording",
                "processing": self.phase == "processing",
                "elapsed": round(elapsed, 1),
                "bytes": size,
                "free_bytes": shutil.disk_usage(self.folder).free,
                "error": self.last_error,
                "result": dict(self.last_result) if self.last_result else None,
                "preview_ready": self.preview_jpeg is not None,
                "preview_active": (
                    self.preview_worker is not None
                    and self.preview_worker.is_alive()
                    and self.preview_process is not None
                    and self.preview_process.poll() is None
                ),
                "preview_age": (
                    round(max(0.0, time.monotonic() - self.preview_stamp), 2)
                    if self.preview_stamp is not None
                    else None
                ),
                "preview_error": self.preview_error,
            }

    def start(self) -> dict[str, Any]:
        with self.lock:
            if self.worker is not None and self.worker.is_alive():
                raise HTTPException(409, "La camara ELP ya esta grabando o procesando")
            if not os.path.exists(self.device):
                raise HTTPException(503, "La camara ELP no esta disponible")
            if shutil.disk_usage(self.folder).free < MIN_FREE_BYTES:
                raise HTTPException(
                    507,
                    "Se requieren al menos 700 MB libres para grabar y generar el proxy",
                )

        self._stop_preview()
        with self.lock:
            if self.worker is not None and self.worker.is_alive():
                raise HTTPException(409, "La camara ELP ya esta grabando o procesando")
            capture_id = time.strftime("%Y%m%d_%H%M%S") + "_" + uuid.uuid4().hex[:8]
            self.master_path = self.folder / f"elp_master_{capture_id}.mkv"
            self.proxy_path = self.folder / f"elp_{capture_id}.mp4"
            self.started_at = time.monotonic()
            self.stop_requested = False
            self.phase = "recording"
            self.last_error = None
            self.last_result = None
            self.worker = threading.Thread(
                target=self._capture_and_process,
                name="elp-camera-recorder",
                daemon=True,
            )
            self.worker.start()
        return self.status()

    def ensure_preview(self) -> None:
        with self.lock:
            if self.phase == "recording":
                return
            if self.preview_worker is not None and self.preview_worker.is_alive():
                return
            if not os.path.exists(self.device):
                return
            self.preview_stop.clear()
            self.preview_error = None
            self.preview_worker = threading.Thread(
                target=self._preview_loop,
                name="elp-camera-preview",
                daemon=True,
            )
            self.preview_worker.start()

    def preview_frame(self) -> tuple[bytes | None, float | None]:
        with self.lock:
            return self.preview_jpeg, self.preview_stamp

    def _stop_preview(self) -> None:
        self.preview_stop.set()
        with self.lock:
            process = self.preview_process
            worker = self.preview_worker
        if process is not None and process.poll() is None:
            process.terminate()
            try:
                process.wait(timeout=3)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait(timeout=2)
        if worker is not None and worker is not threading.current_thread():
            worker.join(timeout=3)
        with self.lock:
            self.preview_process = None
            self.preview_worker = None

    def _preview_loop(self) -> None:
        command = [
            "ffmpeg",
            "-nostdin",
            "-hide_banner",
            "-loglevel",
            "error",
            "-f",
            "v4l2",
            "-input_format",
            "mjpeg",
            "-video_size",
            "640x480",
            "-framerate",
            "30",
            "-i",
            self.device,
            "-an",
            "-c:v",
            "copy",
            "-f",
            "image2pipe",
            "pipe:1",
        ]
        process: subprocess.Popen[bytes] | None = None
        try:
            process = subprocess.Popen(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.DEVNULL,
                bufsize=0,
            )
            with self.lock:
                self.preview_process = process
            if self.preview_stop.is_set():
                process.terminate()
            buffer = bytearray()
            while not self.preview_stop.is_set() and process.poll() is None:
                if process.stdout is None:
                    raise RuntimeError("ffmpeg no expuso el feed ELP")
                chunk = process.stdout.read(65536)
                if not chunk:
                    break
                buffer.extend(chunk)
                while True:
                    start = buffer.find(b"\xff\xd8")
                    end = buffer.find(b"\xff\xd9", start + 2) if start >= 0 else -1
                    if start < 0 or end < 0:
                        if len(buffer) > 4 * 1024 * 1024:
                            del buffer[:-2]
                        break
                    frame = bytes(buffer[start:end + 2])
                    del buffer[:end + 2]
                    with self.lock:
                        self.preview_jpeg = frame
                        self.preview_stamp = time.monotonic()
                        self.preview_error = None
            if not self.preview_stop.is_set() and process.returncode not in (None, 0):
                raise RuntimeError(f"ffmpeg preview termino con codigo {process.returncode}")
        except (OSError, RuntimeError) as exc:
            with self.lock:
                self.preview_error = f"No se pudo abrir el feed ELP: {exc}"
        finally:
            if process is not None and process.poll() is None:
                process.terminate()
                try:
                    process.wait(timeout=3)
                except subprocess.TimeoutExpired:
                    process.kill()
            with self.lock:
                if self.preview_process is process:
                    self.preview_process = None

    def stop(self) -> dict[str, Any]:
        with self.lock:
            if self.phase != "recording":
                raise HTTPException(409, "La camara ELP no esta grabando")
            self.stop_requested = True
            process = self.process
        if process is not None and process.poll() is None:
            process.terminate()
        return self.status()

    def _capture_and_process(self) -> None:
        master = self.master_path
        proxy = self.proxy_path
        if master is None or proxy is None:
            self._fail("No se asignaron rutas para la grabacion ELP")
            return

        log_path = master.with_suffix(".capture.log")
        capture = [
            "ffmpeg",
            "-nostdin",
            "-hide_banner",
            "-loglevel",
            "warning",
            "-f",
            "v4l2",
            "-input_format",
            "mjpeg",
            "-video_size",
            "1920x1080",
            "-framerate",
            "90",
            "-i",
            self.device,
            "-t",
            str(CAPTURE_SECONDS),
            "-an",
            "-c:v",
            "copy",
            "-y",
            str(master),
        ]
        try:
            with log_path.open("wb") as log:
                process = subprocess.Popen(capture, stdout=subprocess.DEVNULL, stderr=log)
                with self.lock:
                    self.process = process
                    stop_requested = self.stop_requested
                if stop_requested and process.poll() is None:
                    process.terminate()
                return_code = process.wait(timeout=CAPTURE_SECONDS + 10)

            if not master.exists() or master.stat().st_size == 0:
                detail = self._read_capture_error(log_path)
                raise RuntimeError(detail or f"ffmpeg termino con codigo {return_code}")

            with self.lock:
                self.process = None
                self.phase = "processing"
            self.ensure_preview()

            master_info = probe(master, count_frames=True)
            if master_info["duration"] <= 0 or master_info.get("frames", 0) < 2:
                raise RuntimeError("La captura ELP no contiene suficientes fotogramas")

            subprocess.run(
                [
                    "ffmpeg",
                    "-nostdin",
                    "-hide_banner",
                    "-loglevel",
                    "error",
                    "-i",
                    str(master),
                    "-vf",
                    "scale=960:-2",
                    "-an",
                    "-c:v",
                    "libx264",
                    "-preset",
                    "ultrafast",
                    "-crf",
                    "20",
                    "-r",
                    "90",
                    "-pix_fmt",
                    "yuv420p",
                    "-movflags",
                    "+faststart",
                    "-y",
                    str(proxy),
                ],
                check=True,
                timeout=90,
                capture_output=True,
            )
            proxy_info = probe(proxy, count_frames=True)
            metadata = {
                "file": proxy.name,
                "url": f"/api/media/{proxy.name}",
                "source": "elp",
                "master_file": master.name,
                "master_url": f"/api/media/{master.name}",
                "master_bytes": master.stat().st_size,
                **proxy_info,
            }
            proxy.with_suffix(proxy.suffix + ".info.json").write_text(
                json.dumps(metadata),
                encoding="utf-8",
            )
            log_path.unlink(missing_ok=True)
            with self.lock:
                self.phase = "ready"
                self.last_result = metadata
                self.last_error = None
        except (OSError, RuntimeError, subprocess.SubprocessError) as exc:
            proxy.unlink(missing_ok=True)
            master.unlink(missing_ok=True)
            self._fail(f"No se pudo completar la grabacion ELP: {exc}")
        finally:
            with self.lock:
                self.process = None
                self.started_at = None
            self.ensure_preview()

    def _fail(self, detail: str) -> None:
        with self.lock:
            self.phase = "error"
            self.last_error = detail
            self.last_result = None

    @staticmethod
    def _read_capture_error(log_path: Path) -> str:
        try:
            return log_path.read_text(encoding="utf-8", errors="replace")[-800:].strip()
        except OSError:
            return ""


def install_routes(app: FastAPI, media_dir: str) -> ElpRecorder:
    recorder = ElpRecorder(media_dir)

    @app.get("/api/elp/status")
    async def elp_status() -> dict[str, Any]:
        return recorder.status()

    async def preview_frames():
        recorder.ensure_preview()
        last_stamp = None
        while True:
            frame, stamp = recorder.preview_frame()
            if frame is not None and stamp != last_stamp:
                last_stamp = stamp
                yield (
                    b"--frame\r\nContent-Type: image/jpeg\r\n"
                    + f"Content-Length: {len(frame)}\r\n\r\n".encode("ascii")
                    + frame
                    + b"\r\n"
                )
            recorder.ensure_preview()
            await asyncio.sleep(0.04)

    @app.get("/api/elp/preview.mjpg")
    async def elp_preview() -> StreamingResponse:
        return StreamingResponse(
            preview_frames(),
            media_type="multipart/x-mixed-replace; boundary=frame",
            headers={"Cache-Control": "no-store, no-cache, must-revalidate"},
        )

    @app.post("/api/elp/recording")
    async def elp_recording(payload: dict[str, Any]) -> dict[str, Any]:
        action = str(payload.get("action", "")).strip().lower()
        if action == "start":
            return recorder.start()
        if action == "stop":
            return recorder.stop()
        raise HTTPException(400, "Usa start o stop")

    return recorder
