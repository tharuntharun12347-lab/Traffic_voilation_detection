# Training and release workflow

This guide continues the existing Roadwatch demo. It does not rebuild the browser app from scratch. The prepared YOLO-format dataset is included at `data/processed/yolo-data/`; after cloning, install Git LFS and run `git lfs pull`. The original source package is available from the Mendeley record cited in [data/DATASET_AND_LIMITATIONS.md](../../../data/DATASET_AND_LIMITATIONS.md).

## Environment

Use Python 3.12. Create a virtual environment and install the dependencies:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r outputs\traffic-watch\training\requirements.txt
```

For CPU training, install the CPU build of PyTorch appropriate for the machine. Training runs locally and can take several hours.

## Prepare the image dataset

The included converted dataset is ready at `data\processed\yolo-data\traffic.yaml`. To reproduce the conversion from the original COCO package, extract its `augmented_dataset` directory with `train`, `valid`, and `test` subfolders, then convert the COCO boxes to YOLO format:

```powershell
python outputs\traffic-watch\training\prepare_yolo_data.py `
  --dataset-root "outputs\.roadwatch-training\source\Traffic Rule Violation Detection Dataset in Dhaka\traffic_violation\augmented_dataset" `
  --output "outputs\.roadwatch-training\yolo-data"
```

The converter preserves all three splits. The expected dataset has 4,644 train images, 117 validation images, and 78 held-out test images. Use validation for training-time checks; do not train on or select checkpoints using the test split.

## Train and evaluate

Start a fresh YOLO11n run using the full training set:

```powershell
python outputs\traffic-watch\training\train_yolo.py `
  --data "data\processed\yolo-data\traffic.yaml" `
  --model "yolo11n.pt" --epochs 8 --imgsz 512 --batch 8 --device cpu `
  --project "outputs\.roadwatch-training\runs" --name roadwatch-yolo11n-full-8ep
```

The best checkpoint is saved under the run's `weights\best.pt`. Evaluate on the held-out test split and export to a temporary candidate path:

```powershell
python outputs\traffic-watch\training\evaluate_export_yolo.py `
  --weights "outputs\.roadwatch-training\runs\roadwatch-yolo11n-full-8ep\weights\best.pt" `
  --data "data\processed\yolo-data\traffic.yaml" `
  --output "outputs\.roadwatch-training\roadwatch-yolo-candidate.onnx" --imgsz 512 `
  --report "outputs\traffic-watch\training\model-evaluation-full-data-candidate.md"
```

Compare overall mAP@50 and the motorcycle, helmet-on, no-helmet, rider, and triple-riding class results against `model-evaluation.md`. This command saves the candidate metrics to a separate report and leaves the deployed model report intact. Keep the existing browser model unless the held-out results justify replacing it without an unacceptable class regression. The 78-image test set is small; report results as preliminary.

## Update and package the page

Whenever a new evaluation report is delivered, update the learning panel from that report and the matching training history, rebuild the standalone page and ZIP, and open the refreshed page preview. Check that the panel's headline and per-class values match the report before sharing it. Keep the report, panel, standalone page, and ZIP in sync as one release.

When a candidate is accepted, copy it to `outputs\traffic-watch\roadwatch-yolo.onnx`, then update the learning panel using that run's validation history. Rebuild the standalone page first, then the ZIP:

```powershell
python outputs\traffic-watch\training\build_performance_panel.py `
  --evaluation outputs\traffic-watch\training\model-evaluation.md `
  --history "outputs\.roadwatch-training\runs\roadwatch-yolo11n-full-8ep\results.csv"
python outputs\traffic-watch\training\package_browser_demo.py
python outputs\traffic-watch\training\build_release.py
```

`package_browser_demo.py` embeds the app, model, and sample clip in the standalone `index.html`. `build_release.py` writes `outputs\roadwatch-website.zip`.

## Data credit and limits

Traffic Rule Violation Detection Dataset in Dhaka Urban Traffic Environment, v1. Authors: Ashesh Bar, Manobendra Biswas, Abir Hasan, Marufur Rahman Mithu, Faisal Ahmad, and Tonmoy Das. Mendeley Data, DOI [10.17632/ycv2mbph4b.1](https://doi.org/10.17632/ycv2mbph4b.1), CC BY-NC 4.0. The data contains labeled images, not labeled videos. Do not use the dataset or derived model commercially without separate permission and preserve attribution when sharing.

Roadwatch does not assess red-light crossing. Uploaded clips are sampled for image inference, with no temporal training or crossing analysis. Detections can miss or miscount unseen examples and require human review.

