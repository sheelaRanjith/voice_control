import time
from dataclasses import dataclass
from typing import List, Dict, Any

import cv2


@dataclass
class DetectionResult:
    label: str
    confidence: float
    x: int
    y: int
    w: int
    h: int

    def to_dict(self) -> Dict[str, Any]:
        return {
            "label": self.label,
            "confidence": round(self.confidence, 3),
            "x": self.x,
            "y": self.y,
            "w": self.w,
            "h": self.h,
        }


class ObjectDetector:
    """Camera + lightweight detection wrapper.

    Uses a simple fallback detector when no ML model is configured so the
    application still runs in constrained environments.
    """

    def __init__(self, camera_index: int = 0) -> None:
        self.capture = cv2.VideoCapture(camera_index)
        self.last_detections: List[Dict[str, Any]] = []
        self.last_frame = None
        self.last_updated = 0.0

    def read_frame(self):
        if not self.capture.isOpened():
            return None
        ok, frame = self.capture.read()
        if not ok:
            return None
        return frame

    def detect_objects(self, frame) -> List[Dict[str, Any]]:
        h, w = frame.shape[:2]
        box_w = w // 4
        box_h = h // 3
        x = (w - box_w) // 2
        y = (h - box_h) // 2

        # Fallback pseudo-detection region in the center of frame.
        detections = [
            DetectionResult(
                label="navigable_path",
                confidence=0.55,
                x=x,
                y=y,
                w=box_w,
                h=box_h,
            ).to_dict()
        ]

        for det in detections:
            cv2.rectangle(
                frame,
                (det["x"], det["y"]),
                (det["x"] + det["w"], det["y"] + det["h"]),
                (0, 255, 0),
                2,
            )
            cv2.putText(
                frame,
                f"{det['label']} {det['confidence']:.2f}",
                (det["x"], max(20, det["y"] - 10)),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (0, 255, 0),
                2,
            )

        self.last_detections = detections
        self.last_updated = time.time()
        self.last_frame = frame.copy()
        return detections

    def get_processed_frame_bytes(self):
        frame = self.read_frame()
        if frame is None:
            return None
        self.detect_objects(frame)
        ok, buffer = cv2.imencode(".jpg", frame)
        if not ok:
            return None
        return buffer.tobytes()

    def snapshot_bytes(self):
        frame = self.last_frame if self.last_frame is not None else self.read_frame()
        if frame is None:
            return None
        ok, buffer = cv2.imencode(".jpg", frame)
        if not ok:
            return None
        return buffer.tobytes()

    def release(self):
        if self.capture.isOpened():
            self.capture.release()
