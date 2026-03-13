# Voice-Controlled Real-Time Smart Vision System

Production-style full-stack project with:
- **Backend (Flask + YOLOv8 + pyttsx3)** for real-time detection, command intent processing, and voice guidance.
- **Frontend (React + Bootstrap)** for live feed, detections, confidence bars, and command controls.

## Project structure

```text
voice_control/
  backend/
    app.py
    detector.py
    voice.py
    tts.py
    train_model.py
    dataset_config.example.yaml
    requirements.txt
  frontend/
    public/index.html
    src/
      App.js
      VideoFeed.js
      ObjectList.js
      VoiceControl.js
      NavigationPanel.js
      index.js
      styles.css
    package.json
```

## Backend setup
This project contains:

- `backend/` – Flask API for camera streaming, object detection state, voice commands, and navigation feedback.
- `frontend/` – React UI for live feed, object list, voice control, and guidance panels.

## 1) Backend setup and run

From the repo root:

```bash
cd backend
python -m venv .venv
# Linux/macOS
source .venv/bin/activate
# Windows PowerShell
# .\.venv\Scripts\Activate.ps1
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
python app.py
```

Backend runs at: `http://localhost:8000`

### Backend APIs

- `GET /video_feed` — MJPEG stream with YOLOv8 bounding boxes.
- `GET /detect_objects` — list of current detections.
- `POST /voice_command` — process text/audio command.
- `GET /navigation_feedback` — last generated guidance.
- `GET /snapshot` — latest annotated frame.
- `GET /status` — backend/camera/FPS/status diagnostics.
- `GET /health` — simple health check.

## Frontend setup
Backend runs on `http://localhost:8000` by default.

### Backend endpoints

- `GET /video_feed` – MJPEG stream.
- `GET /detect_objects` – Latest object detections.
- `POST /voice_command` – Accepts `{ "transcript": "..." }` JSON or an uploaded `audio` file.
- `GET /navigation_feedback` – Text guidance built from last command + detections.
- `GET /snapshot` – Latest JPEG snapshot.

## 2) Frontend setup and run

In a second terminal:

```bash
cd frontend
npm install
npm start
```

Frontend: `http://localhost:3000`

If backend URL differs:
Frontend runs on `http://localhost:3000`.

If backend is not on default host/port, set:

```bash
export REACT_APP_BACKEND_URL=http://localhost:8000
npm start
```

## Voice commands supported

- `find person`
- `find chair`
- `detect objects`
- `navigate left`
- `navigate right`
- `navigate forward`
- `navigate backward`

The backend returns:
- intent (`find` / `detect` / `navigate`)
- feedback text
- matched objects
- all current objects with confidence + approximate position (`left/center/right`) and distance hint (`near/medium/far`)

## YOLO training helper

```bash
cd backend
python train_model.py --data dataset.yaml --model yolov8n.pt --epochs 50
```

Use `backend/dataset_config.example.yaml` as template.

## Testing live detection

1. Start backend (`python app.py`).
2. Start frontend (`npm start`).
3. Click **Start** in UI.
4. Verify camera stream + boxes appear.
5. Use **Speak Command** or text command input.
6. Verify command feedback and detected objects panel updates.

## Troubleshooting

### `ImportError: numpy.core.multiarray failed to import`

This is a NumPy/OpenCV binary mismatch. Use clean venv and install pinned deps in `backend/requirements.txt`.

### Browser speech recognition unavailable

Use the text command input in `VoiceControl`.

### No audio from pyttsx3

Server/container may not expose an audio device. API still returns text guidance in JSON.

## Optional enhancements

- Save periodic snapshots from `/snapshot` to disk.
- Add multilingual TTS/ASR pipeline.
- Mobile camera feed support by replacing webcam input with RTSP/WebRTC source.


### `SyntaxError: name '_last_command' is used prior to global declaration`

Use the latest `backend/app.py`. The backend now stores runtime values in a shared `_state` dictionary (no `global` declarations needed), which removes this error source.

### `OSError: [WinError 10038]` while stopping/restarting Flask

Run backend without the Werkzeug reloader:

```powershell
cd .\backend
python app.py
```

This project now starts Flask with `use_reloader=False` by default to avoid duplicate-socket/reloader issues on Windows.

For a more production setup on Windows, run with Waitress:

```powershell
pip install waitress
python -m waitress --listen=0.0.0.0:8000 app:app
```
## 3) Model training script (fix for missing file error)

If you ran `python train_model.py` and got `No such file or directory`, pull the latest code and run from inside `backend/` where `train_model.py` now exists.

### Linux/macOS

```bash
cd backend
python train_model.py --help
python train_model.py --data dataset.yaml --model yolov8n.pt --epochs 50
```

### Windows PowerShell

```powershell
cd .\backend
python .\train_model.py --help
python .\train_model.py --data .\dataset.yaml --model yolov8n.pt --epochs 50
```

Dataset config example is included at:

- `backend/dataset_config.example.yaml`

Copy it to your own `dataset.yaml` and update paths/classes.

## 4) How to use in the UI

1. Open `http://localhost:3000`.
2. Click **Start** to begin live feed and polling.
3. Use **Speak Command** to send a voice command (browser SpeechRecognition API).
4. Check:
   - **Detected Objects** panel,
   - **Voice Command Status**,
   - **Navigation Feedback**.
5. Use **Snapshot** to fetch a still frame.
6. Use **Stop** to pause live updates and **Reset** to clear UI state.

## Notes

- Camera access permission is required by your OS/browser.
- `SpeechRecognition` support depends on browser (typically Chromium-based).
- Current detector is a fallback placeholder region for scaffold/demo usage; replace with YOLOv8/MobileNet SSD logic in `backend/detector.py` for production-grade detection.
