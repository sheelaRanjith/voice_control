from __future__ import annotations

import io
import re
from typing import Dict, Optional

import speech_recognition as sr


COMMAND_PATTERNS = {
    "find": re.compile(r"\b(find|locate|where is)\s+(?P<object>[a-zA-Z0-9_ ]+)"),
    "detect": re.compile(r"\b(detect|scan|what do you see)\b"),
    "navigate": re.compile(r"\b(navigate|go|move|turn)\s+(?P<direction>left|right|forward|backward|back)"),
}


class VoiceRecognizer:
    def __init__(self) -> None:
        self.recognizer = sr.Recognizer()

    def recognize_audio_bytes(self, audio_bytes: bytes) -> Optional[str]:
        try:
            with sr.AudioFile(io.BytesIO(audio_bytes)) as source:
                audio = self.recognizer.record(source)
            return self.recognizer.recognize_google(audio)
        except Exception:
            return None

    @staticmethod
    def normalize_command(text: str) -> str:
        return " ".join(text.strip().lower().split())

    def parse_intent(self, text: str) -> Dict[str, str]:
        normalized = self.normalize_command(text)

        match_find = COMMAND_PATTERNS["find"].search(normalized)
        if match_find:
            return {"intent": "find", "target": match_find.group("object").strip(), "raw": normalized}

        if COMMAND_PATTERNS["detect"].search(normalized):
            return {"intent": "detect", "target": "", "raw": normalized}

        match_nav = COMMAND_PATTERNS["navigate"].search(normalized)
        if match_nav:
            direction = match_nav.group("direction").replace("back", "backward")
            return {"intent": "navigate", "target": direction, "raw": normalized}

        return {"intent": "unknown", "target": "", "raw": normalized}
