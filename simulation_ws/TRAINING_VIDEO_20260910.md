# Kinect and phone swing review

Open http://192.168.40.74:8080/ and select Entrenamiento. Home Assistant
smart-trolley embeds this same interface; refresh to load new assets.

Kinect capture timer is now configurable, default 30 Hz (previously ~15 Hz).
Point clouds are computed only when subscribed. Preview remains throttled to
4 Hz; recording consumes incoming RGB frames at native 640x480, JPEG quality 85.
Clips stop collecting at 30 s or 900 frames. Press Guardar Kinect to finalize.
AVI original and relative capture timestamps are retained. An MP4 H.264 copy
is created for browser playback, at the measured average capture rate; timing
jitter remains available in the timestamps sidecar.

Validated on Pi: 104 frames in ~4 s, 25.81 fps recording; received RGB 26 fps.
This is not a promise of sustained 30 fps. Live posture analysis remains capped
at 10 Hz while recording and 2 Hz idle. Low-visibility body landmarks are
rejected and angles account for image aspect ratio. No calibrated 3D joint
measurements, club speed, ball speed, or automatic impact measurement.

Phone uploads: MP4/MOV/M4V/WebM, 300 MB per upload, one upload at a time.
Original bytes are retained; ffprobe validates video and reports file fps.
Browser codec support varies; export H.264 MP4 if the original cannot play.
Library, slow playback, approximate frame stepping, manual top/impact markers,
and JSON marker export are available. Phone analysis is manual in this release.
Slow-motion exports may have retimed playback: marker seconds refer to the
file timeline, not necessarily elapsed physical swing time.

Tests: valid synthetic 120 fps MP4 upload/list passed; invalid MP4 rejected;
four-second real Kinect recording and MP4 conversion passed. Python syntax,
JavaScript syntax and all three ROS builds passed. Browser visual inspection
has not been performed in this session.

Pre-change backups on Pi: robot_backups/operator_web_pre_training_20260910,
kinect_pre_30fps_20260910.cpp, swing_pre_training_20260910.py.
