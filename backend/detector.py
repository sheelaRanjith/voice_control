from __future__ import annotations

import threading
import time
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

import cv2
from ultralytics import YOLO


@dataclass
class DetectionResult:
    label: str
    confidence: float
    x: int
    y: int
    w: int
    h: int
    center_x: int
    center_y: int
    position: str
    distance_hint: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "label": self.label,
            "confidence": round(self.confidence, 3),
            "x": self.x,
            "y": self.y,
            "w": self.w,
            "h": self.h,
            "center_x": self.center_x,
            "center_y": self.center_y,
            "position": self.position,
            "distance_hint": self.distance_hint,
        }


class RealtimeDetector:
    def __init__(self, camera_index: int = 0, model_path: str = "yolov8n.pt", conf: float = 0.35) -> None:
        self.camera_index = camera_index
        self.conf = conf
        self.model = YOLO(model_path)
        self.capture = cv2.VideoCapture(camera_index)

        self.lock = threading.Lock()
        self.running = False
        self.thread: Optional[threading.Thread] = None

        self.last_frame_jpeg: Optional[bytes] = None
        self.last_raw_frame = None
        self.last_detections: List[Dict[str, Any]] = []
        self.last_updated = 0.0
        self.last_error = ""
        self.fps = 0.0

    def start(self) -> None:
        if self.running:
            return
        self.running = True
        self.thread = threading.Thread(target=self._loop, daemon=True)
        self.thread.start()

    def _classify_position(self, x_center: float, frame_width: int) -> str:
        ratio = x_center / max(frame_width, 1)
        if ratio < 0.33:
            return "left"
        if ratio > 0.66:
            return "right"
        return "center"

    def _distance_hint(self, box_area: float, frame_area: float) -> str:
        ratio = box_area / max(frame_area, 1)
        if ratio > 0.20:
            return "near"
        if ratio > 0.06:
            return "medium"
        return "far"

    def _loop(self) -> None:
        prev = time.time()
        while self.running:
            ok, frame = self.capture.read()
            if not ok:
                self.last_error = "Unable to read from camera"
                time.sleep(0.05)
                continue

            detections: List[Dict[str, Any]] = []
            frame_h, frame_w = frame.shape[:2]
            frame_area = frame_h * frame_w
            result = self.model.predict(source=frame, conf=self.conf, verbose=False)[0]

            for box in result.boxes:
                cls_id = int(box.cls[0])
                conf = float(box.conf[0])
                x1, y1, x2, y2 = [int(v) for v in box.xyxy[0].tolist()]
                w = max(0, x2 - x1)
                h = max(0, y2 - y1)
                center_x = x1 + w // 2
                center_y = y1 + h // 2
                label = self.model.names.get(cls_id, str(cls_id))
                position = self._classify_position(center_x, frame_w)
                distance_hint = self._distance_hint(w * h, frame_area)

                det = DetectionResult(
                    label=label,
                    confidence=conf,
                    x=x1,
                    y=y1,
                    w=w,
                    h=h,
                    center_x=center_x,
                    center_y=center_y,
                    position=position,
                    distance_hint=distance_hint,
                )
                detections.append(det.to_dict())

                color = (0, 200, 0)
                cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
                cv2.putText(
                    frame,
                    f"{label} {conf:.2f} {position}/{distance_hint}",
                    (x1, max(20, y1 - 10)),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.55,
                    color,
                    2,
                )

            now = time.time()
            dt = now - prev
            if dt > 0:
                self.fps = 0.9 * self.fps + 0.1 * (1.0 / dt) if self.fps else (1.0 / dt)
            prev = now

            cv2.putText(frame, f"FPS: {self.fps:.1f}", (15, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 0), 2)
            ok_jpg, encoded = cv2.imencode(".jpg", frame)
            if not ok_jpg:
                continue

            with self.lock:
                self.last_raw_frame = frame.copy()
                self.last_frame_jpeg = encoded.tobytes()
                self.last_detections = detections
                self.last_updated = now
                self.last_error = ""

    def get_frame_jpeg(self) -> Optional[bytes]:
        with self.lock:
            return self.last_frame_jpeg

    def get_detections(self) -> List[Dict[str, Any]]:
        with self.lock:
            return list(self.last_detections)

    def snapshot_jpeg(self) -> Optional[bytes]:
        with self.lock:
            return self.last_frame_jpeg

    def status(self) -> Dict[str, Any]:
        return {
            "running": self.running,
            "camera_open": self.capture.isOpened(),
            "fps": round(self.fps, 2),
            "last_updated": self.last_updated,
            "last_error": self.last_error,
            "detections_count": len(self.last_detections),
        }

    def stop(self) -> None:
        self.running = False
        if self.thread and self.thread.is_alive():
            self.thread.join(timeout=2)
        if self.capture.isOpened():
            self.capture.release()
