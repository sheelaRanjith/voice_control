from __future__ import annotations

from typing import Dict, List, Tuple

import pyttsx3


class SpeechSynthesizer:
    def __init__(self, language: str = "en") -> None:
        self.engine = pyttsx3.init()
        self.language = language
        self.engine.setProperty("rate", 170)

    def speak(self, text: str) -> None:
        try:
            self.engine.say(text)
            self.engine.runAndWait()
        except Exception:
            # Keep API non-blocking even if local audio output is unavailable.
            pass


def build_guidance(intent: Dict[str, str], detections: List[Dict]) -> Tuple[str, List[Dict]]:
    intent_name = intent.get("intent", "unknown")
    target = intent.get("target", "")

    if intent_name == "find":
        matches = [d for d in detections if target in d["label"].lower()]
        if not matches:
            return f"I cannot see {target} right now.", []
        top = sorted(matches, key=lambda d: d["confidence"], reverse=True)[0]
        return (
            f"{top['label']} detected on the {top['position']} at {top['distance_hint']} distance.",
            matches,
        )

    if intent_name == "detect":
        if not detections:
            return "No objects detected.", []
        names = ", ".join(sorted({d["label"] for d in detections}))
        return f"I can see: {names}.", detections

    if intent_name == "navigate":
        if target in {"left", "right", "forward", "backward"}:
            return f"Navigation command received. Move {target} carefully.", detections
        return "Navigation command not understood.", detections

    return "Command not recognized. Try find person or detect objects.", detections
from typing import List, Dict


def build_navigation_feedback(last_command: str, detections: List[Dict]) -> str:
    if not detections:
        return "No objects detected. Proceed cautiously."

    labels = ", ".join(sorted({det['label'] for det in detections}))

    if "left" in last_command:
        return f"Turning left. Nearby detections: {labels}."
    if "right" in last_command:
        return f"Turning right. Nearby detections: {labels}."
    if "stop" in last_command:
        return f"Stop command acknowledged. Monitoring: {labels}."
    return f"Detected: {labels}. Continue forward."
