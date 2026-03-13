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

```bash
cd backend
python -m venv .venv
# Linux/macOS
source .venv/bin/activate
# Windows PowerShell
# .\.venv\Scripts\Activate.ps1
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

```bash
cd frontend
npm install
npm start
```

Frontend: `http://localhost:3000`

If backend URL differs:

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


### Better find accuracy (calendar / water bottle)

- `find water bottle` now maps to YOLO label `bottle`.
- `find calendar` uses alias matching (`calendar`, `clock`, `book`) because COCO models usually do not have a dedicated `calendar` class.
- If browser speech recognition hears a wrong word, use **text command** or **Upload Audio** in UI for better control.


### `SyntaxError: invalid decimal literal` with `>>>>>>>` in `app.py`

Your local file still contains unresolved Git merge conflict markers.

Check and clean markers:

```powershell
cd .\backend
findstr /n "<<<<<<< ======= >>>>>>>" app.py
```

Then either:
1. discard local conflicted file and restore from git, or
2. manually remove `<<<<<<<`, `=======`, `>>>>>>>` blocks and keep the correct code.

Quick restore (if you want repo version):

```powershell
cd ..
git checkout -- backend/app.py
python backend/app.py
```


If you want an automatic local repair, use the helper script in this repo:

```powershell
cd ..
python scripts/repair_merge_conflicts.py backend/app.py --take ours
python backend/app.py
```

(Use `--take theirs` if you want to keep the lower half of each conflict block.)


### `_pickle.UnpicklingError: Weights only load failed` (PyTorch 2.6+)

PyTorch 2.6 changed default `torch.load(..., weights_only=True)` behavior and some YOLO checkpoints fail to load.

This repo now includes two protections:
- `backend/requirements.txt` pins `torch<2.6`
- `backend/detector.py` applies a compatibility fallback (`add_safe_globals` + `TORCH_FORCE_NO_WEIGHTS_ONLY_LOAD`) before retrying model load.

Recommended fix in existing venv:

```powershell
cd .\backend
pip uninstall -y torch torchvision torchaudio
pip install "torch<2.6"
pip install -r requirements.txt
python app.py
```


### Voice speaks only once and then becomes silent

`pyttsx3` can sometimes stop responding after the first `runAndWait()` call in long-running Flask apps.

This repo now uses an async TTS queue worker (`SpeechSynthesizer`) that keeps speaking across repeated commands (`find`, `detect`, `navigate`).

If you still face issues on Windows:

```powershell
cd .\backend
python app.py
```

and avoid running multiple app instances at the same time.


### Frontend audio not audible (`audio kekkala`)

The UI now has a browser-side **Audio On/Off** toggle.
When a command response arrives, the frontend uses `window.speechSynthesis` to speak feedback on the user's machine.

If still silent:
- click anywhere on the page once (some browsers require user interaction before audio),
- keep Audio set to `On`,
- check system/browser volume and output device.


### Audio plays only first time / no audio for second `find`

Frontend now includes:
- forced re-speak for every new command response,
- **Replay Audio** button in Navigation Feedback panel,
- `Detected At` time badge for `detect objects` visibility.

If repeated audio still fails, click **Replay Audio** and interact once on page (browser autoplay policy).
