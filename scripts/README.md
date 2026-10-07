# Training and data scripts

These are the model/data scripts used for RoadWatch. Dataset files are not included; obtain the licensed dataset separately. The release-panel and website packaging helpers remain alongside the demo in `outputs/traffic-watch/training/` so the downloadable demo can be rebuilt in place.

Typical commands from the repository root:

```powershell
python scripts/prepare_yolo_data.py --dataset-root "data/source/augmented_dataset" --output "data/processed/yolo-data"
python scripts/train_yolo.py --data "data/processed/yolo-data/traffic.yaml" --model yolo11n.pt --epochs 8 --imgsz 512 --batch 8 --device cpu --project runs --name roadwatch-yolo11n
python scripts/evaluate_export_yolo.py --weights "runs/roadwatch-yolo11n/weights/best.pt" --data "data/processed/yolo-data/traffic.yaml" --output model/roadwatch-yolo.onnx --report results/model-evaluation.md
```

For reproducible training/evaluation details, splits, attribution, and the website rebuild workflow, see `outputs/traffic-watch/training/README.md`.
