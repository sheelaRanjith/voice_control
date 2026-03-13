from __future__ import annotations

import io
from typing import Optional

import speech_recognition as sr


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
        return text.strip().lower()
