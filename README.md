# Voice-Controlled Real-Time Smart Vision System

This project contains:

- `backend/` – Flask API for camera streaming, object detection state, voice commands, and navigation feedback.
- `frontend/` – React UI for live feed, object list, voice control, and guidance panels.

## 1) Backend setup and run

From the repo root:

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
python app.py
```

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

Frontend runs on `http://localhost:3000`.

If backend is not on default host/port, set:

```bash
export REACT_APP_BACKEND_URL=http://localhost:8000
npm start
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
