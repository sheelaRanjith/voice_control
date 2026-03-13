from __future__ import annotations

import atexit
import time
from typing import Generator

from flask import Flask, Response, jsonify, request
from flask_cors import CORS

from detector import ObjectDetector
from tts import build_navigation_feedback
from voice import VoiceRecognizer

app = Flask(__name__)
CORS(app)

_detector = ObjectDetector(camera_index=0)
_voice = VoiceRecognizer()
_last_command = ""


def stream_frames() -> Generator[bytes, None, None]:
    while True:
        frame_bytes = _detector.get_processed_frame_bytes()
        if frame_bytes is None:
            time.sleep(0.05)
            continue
        yield (
            b"--frame\r\n"
            b"Content-Type: image/jpeg\r\n\r\n" + frame_bytes + b"\r\n"
        )


@app.route("/video_feed")
def video_feed() -> Response:
    return Response(stream_frames(), mimetype="multipart/x-mixed-replace; boundary=frame")


@app.route("/detect_objects")
def detect_objects() -> Response:
    return jsonify({"objects": _detector.last_detections, "updated_at": _detector.last_updated})


@app.route("/voice_command", methods=["POST"])
def voice_command() -> Response:
    global _last_command

    payload = request.get_json(silent=True) or {}
    transcript = payload.get("transcript")

    if not transcript and "audio" in request.files:
        audio_file = request.files["audio"]
        transcript = _voice.recognize_audio_bytes(audio_file.read())

    if not transcript:
        return jsonify({"command": "", "status": "no_command"}), 400

    _last_command = _voice.normalize_command(transcript)
    return jsonify({"command": _last_command, "status": "ok"})


@app.route("/navigation_feedback")
def navigation_feedback() -> Response:
    feedback = build_navigation_feedback(_last_command, _detector.last_detections)
    return jsonify({"feedback": feedback, "last_command": _last_command})


@app.route("/snapshot")
def snapshot() -> Response:
    image = _detector.snapshot_bytes()
    if image is None:
        return jsonify({"error": "snapshot unavailable"}), 503
    return Response(image, mimetype="image/jpeg")


@atexit.register
def _cleanup() -> None:
    _detector.release()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
