"""Train a YOLO model for object detection.

Usage examples:
  python train_model.py --data dataset.yaml --model yolov8n.pt --epochs 50
  python train_model.py --data dataset.yaml --model yolov8s.pt --imgsz 640 --batch 16
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Train a YOLO model with Ultralytics.")
    parser.add_argument("--data", required=True, help="Path to dataset YAML file.")
    parser.add_argument("--model", default="yolov8n.pt", help="Base model checkpoint.")
    parser.add_argument("--epochs", type=int, default=50, help="Training epochs.")
    parser.add_argument("--imgsz", type=int, default=640, help="Image size.")
    parser.add_argument("--batch", type=int, default=16, help="Batch size.")
    parser.add_argument("--project", default="runs/train", help="Output project directory.")
    parser.add_argument("--name", default="voice_control_exp", help="Run name.")
    parser.add_argument("--device", default="cpu", help="Device id, e.g. cpu, 0, 0,1")
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    data_path = Path(args.data)
    if not data_path.exists():
        print(f"[ERROR] Dataset YAML not found: {data_path}")
        print("Hint: copy backend/dataset_config.example.yaml and update paths/classes.")
        return 1

    try:
        from ultralytics import YOLO
    except Exception as exc:
        print("[ERROR] ultralytics is not installed.")
        print("Install it with: pip install ultralytics")
        print(f"Details: {exc}")
        return 1

    model = YOLO(args.model)
    results = model.train(
        data=str(data_path),
        epochs=args.epochs,
        imgsz=args.imgsz,
        batch=args.batch,
        project=args.project,
        name=args.name,
        device=args.device,
    )

    print("Training complete.")
    print(results)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
