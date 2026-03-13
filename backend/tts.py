from __future__ import annotations

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
