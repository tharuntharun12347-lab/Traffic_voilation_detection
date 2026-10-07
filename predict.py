"""Run image or video inference with the included RoadWatch YOLO checkpoint."""
from __future__ import annotations

import argparse
from pathlib import Path
from ultralytics import YOLO

ROOT = Path(__file__).resolve().parent


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", help="Image, video, directory, or webcam source accepted by Ultralytics")
    parser.add_argument("--weights", type=Path, default=ROOT / "model" / "weights" / "best.pt")
    parser.add_argument("--conf", type=float, default=0.35, help="Detection confidence threshold")
    parser.add_argument("--imgsz", type=int, default=512)
    parser.add_argument("--device", default="cpu", help="cpu or a CUDA device such as 0")
    parser.add_argument("--project", type=Path, default=ROOT / "results" / "predictions")
    parser.add_argument("--name", default="roadwatch")
    args = parser.parse_args()

    if not args.weights.is_file():
        parser.error(f"Checkpoint not found: {args.weights}")
    model = YOLO(str(args.weights))
    outputs = model.predict(
        source=args.source,
        conf=args.conf,
        imgsz=args.imgsz,
        device=args.device,
        save=True,
        project=str(args.project),
        name=args.name,
        exist_ok=True,
    )
    print(f"Saved predictions for {len(outputs)} input item(s) under {args.project / args.name}")
    print("Results are preliminary; inspect the original media and do not treat missing detections as proof of compliance.")


if __name__ == "__main__":
    main()
