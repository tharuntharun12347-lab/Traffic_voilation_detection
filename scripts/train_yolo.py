from pathlib import Path
import argparse
from ultralytics import YOLO

p = argparse.ArgumentParser(description="Fine-tune YOLO on the traffic-rule dataset")
p.add_argument("--data", required=True, help="YOLO data.yaml made from the dataset")
p.add_argument("--model", default="yolo11n.pt", help="Pretrained YOLO checkpoint")
p.add_argument("--epochs", type=int, default=40)
p.add_argument("--imgsz", type=int, default=512)
p.add_argument("--batch", type=int, default=4)
p.add_argument("--fraction", type=float, default=1.0, help="Fraction of training set to use, between 0 and 1")
p.add_argument("--device", default="cpu", help="cpu or a CUDA device such as 0")
p.add_argument("--project", default="runs")
p.add_argument("--name", default="roadwatch-yolo11n")
a = p.parse_args()

model = YOLO(a.model)
model.train(
    data=a.data, epochs=a.epochs, imgsz=a.imgsz, batch=a.batch,
    device=a.device, workers=0, seed=42, deterministic=True,
    patience=10, close_mosaic=min(8, max(0, a.epochs // 4)), cache=False, plots=True,
    fraction=a.fraction,
    project=a.project, name=a.name,
    fliplr=0.5, flipud=0.0, degrees=4.0, scale=0.25,
    hsv_h=0.015, hsv_s=0.5, hsv_v=0.3,
)

best = Path(model.trainer.save_dir) / "weights" / "best.pt"
if not best.exists():
    raise FileNotFoundError(f"Expected trained checkpoint at {best}")
print(f"Best checkpoint: {best.resolve()}")
print("Held-out evaluation command:")
print(f"yolo detect val model={best} data={a.data} split=test imgsz={a.imgsz} device={a.device}")
