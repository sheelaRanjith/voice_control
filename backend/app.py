from __future__ import annotations

import atexit
import json
import time
from typing import Generator

from flask import Flask, Response, jsonify, request
from flask_cors import CORS

from detector import RealtimeDetector
from tts import SpeechSynthesizer, build_guidance
from detector import ObjectDetector
from tts import build_navigation_feedback
from voice import VoiceRecognizer

app = Flask(__name__)
CORS(app)

_detector = RealtimeDetector(camera_index=0, model_path="yolov8n.pt", conf=0.35)
_detector.start()
_voice = VoiceRecognizer()
_tts = SpeechSynthesizer(language="en")
_state = {"last_command": "", "last_feedback": ""}
_last_command = ""
_last_feedback = ""


def mjpeg_stream() -> Generator[bytes, None, None]:
    while True:
        frame = _detector.get_frame_jpeg()
        if frame is None:
            time.sleep(0.03)
            continue
        yield b"--frame\r\nContent-Type: image/jpeg\r\n\r\n" + frame + b"\r\n"
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
    return Response(mjpeg_stream(), mimetype="multipart/x-mixed-replace; boundary=frame")
    return Response(stream_frames(), mimetype="multipart/x-mixed-replace; boundary=frame")


@app.route("/detect_objects")
def detect_objects() -> Response:
    return jsonify({"objects": _detector.get_detections(), "updated_at": _detector.status()["last_updated"]})


@app.route("/status")
def status() -> Response:
    return jsonify(
        {
            "backend": "ok",
            "detector": _detector.status(),
            "last_command": _state["last_command"],
            "last_feedback": _state["last_feedback"],
        }
    )
            "last_command": _last_command,
            "last_feedback": _last_feedback,
        }
    )
    return jsonify({"objects": _detector.last_detections, "updated_at": _detector.last_updated})


@app.route("/voice_command", methods=["POST"])
def voice_command() -> Response:
    global _last_command, _last_feedback

    payload = request.get_json(silent=True) or {}
    transcript = payload.get("transcript")
    language = payload.get("language", "en")

    if not transcript and "audio" in request.files:
        transcript = _voice.recognize_audio_bytes(request.files["audio"].read())

    if not transcript:
        return jsonify({"status": "no_command", "command": "", "feedback": "No command received."}), 400

    normalized = _voice.normalize_command(transcript)
    intent = _voice.parse_intent(normalized)
    detections = _detector.get_detections()
    feedback, matched = build_guidance(intent, detections)

    _state["last_command"] = normalized
    _state["last_feedback"] = feedback
    _last_command = _voice.normalize_command(transcript)
    intent = _voice.parse_intent(_last_command)
    detections = _detector.get_detections()
    feedback, matched = build_guidance(intent, detections)
    _last_feedback = feedback

    if language:
        _tts.language = language
    _tts.speak(feedback)

    return jsonify(
        {
            "status": "ok",
            "command": normalized,
            "command": _last_command,
            "intent": intent,
            "feedback": feedback,
            "matched_objects": matched,
            "all_objects": detections,
        }
    )
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
    return jsonify({"feedback": _state["last_feedback"], "last_command": _state["last_command"]})
    return jsonify({"feedback": _last_feedback, "last_command": _last_command})
    feedback = build_navigation_feedback(_last_command, _detector.last_detections)
    return jsonify({"feedback": feedback, "last_command": _last_command})


@app.route("/snapshot")
def snapshot() -> Response:
    frame = _detector.snapshot_jpeg()
    if frame is None:
        return jsonify({"error": "snapshot unavailable"}), 503
    return Response(frame, mimetype="image/jpeg")


@app.route("/health")
def health() -> Response:
    return Response(json.dumps({"ok": True}), mimetype="application/json")
    image = _detector.snapshot_bytes()
    if image is None:
        return jsonify({"error": "snapshot unavailable"}), 503
    return Response(image, mimetype="image/jpeg")


@atexit.register
def _cleanup() -> None:
    _detector.stop()


if __name__ == "__main__":
    # `use_reloader=False` avoids duplicate camera/process issues and WinError 10038 socket edge-cases on Windows.
    app.run(host="0.0.0.0", port=8000, threaded=True, debug=False, use_reloader=False)
    app.run(host="0.0.0.0", port=8000, threaded=True, debug=False)
    _detector.release()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
