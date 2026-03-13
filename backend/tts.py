from __future__ import annotations

import queue
import re
import threading
from typing import Dict, List, Optional, Tuple

import pyttsx3


TARGET_ALIASES = {
    "water bottle": ["bottle", "water bottle", "waterbottle"],
    "bottle": ["bottle", "water bottle", "waterbottle"],
    "mobile": ["cell phone", "phone", "mobile"],
    "calendar": ["calendar", "clock", "book"],
}


class SpeechSynthesizer:
    """Thread-safe async TTS queue so voice works for repeated commands."""

    def __init__(self, language: str = "en") -> None:
        self.language = language
        self._engine = self._create_engine()
        self._queue: queue.Queue[Optional[str]] = queue.Queue()
        self._worker = threading.Thread(target=self._run, daemon=True)
        self._worker.start()

    @staticmethod
    def _create_engine():
        engine = pyttsx3.init()
        engine.setProperty("rate", 170)
        return engine

    def _run(self) -> None:
        while True:
            text = self._queue.get()
            if text is None:
                break
            try:
                self._engine.say(text)
                self._engine.runAndWait()
            except Exception:
                # Recreate engine to recover from occasional pyttsx3 one-shot failures.
                try:
                    self._engine.stop()
                except Exception:
                    pass
                try:
                    self._engine = self._create_engine()
                    self._engine.say(text)
                    self._engine.runAndWait()
                except Exception:
                    pass
            finally:
                self._queue.task_done()

    def speak(self, text: str) -> None:
        if text:
            self._queue.put(text)

    def shutdown(self) -> None:
        self._queue.put(None)
        if self._worker.is_alive():
            self._worker.join(timeout=2)


def _normalize_target(target: str) -> str:
    target = target.lower().strip()
    target = re.sub(r"\b(a|an|the)\b", "", target)
    return " ".join(target.split())


def _candidate_terms(target: str) -> List[str]:
    normalized = _normalize_target(target)
    terms = TARGET_ALIASES.get(normalized, [normalized])
    return [t.strip() for t in terms if t.strip()]


def _match_find(target: str, detections: List[Dict]) -> List[Dict]:
    terms = _candidate_terms(target)
    if not terms:
        return []

    exact_matches: List[Dict] = []
    fuzzy_matches: List[Dict] = []

    for det in detections:
        label = det.get("label", "").lower().strip()
        if any(term == label for term in terms):
            exact_matches.append(det)
        elif any(term in label or label in term for term in terms):
            fuzzy_matches.append(det)

    return exact_matches if exact_matches else fuzzy_matches


def build_guidance(intent: Dict[str, str], detections: List[Dict]) -> Tuple[str, List[Dict]]:
    intent_name = intent.get("intent", "unknown")
    target = intent.get("target", "")

    if intent_name == "find":
        matches = _match_find(target, detections)
        if not matches:
            return f"I cannot see {target} right now. Try detect objects to list visible classes.", []
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

    return "Command not recognized. Try find person, find bottle, or detect objects.", detections
