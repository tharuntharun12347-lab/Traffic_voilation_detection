# RoadWatch AI

RoadWatch is a classroom traffic-safety demo. The frontend runs the ONNX YOLO11n model in the browser. The FastAPI backend serves the frontend and exposes image/video prediction endpoints using the included YOLO checkpoint. Both paths provide preliminary detections for human review.

## Install and run

Use Python 3.12 and a modern browser. The browser app loads ONNX Runtime Web from its CDN, so keep an internet connection available.

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
Copy-Item .env.example .env
python -m uvicorn backend.main:app --reload --host 127.0.0.1 --port 8000
```

Open `http://127.0.0.1:8000/` for the frontend and `http://127.0.0.1:8000/docs` for interactive API docs. The current frontend continues to run browser inference; backend prediction endpoints are available to other clients and for future UI integration. See [`backend/README.md`](backend/README.md) for endpoints and upload limits.

For the static frontend without the API, `python serve.py` serves the source app. For command-line prediction:

```powershell
python predict.py path\to\image.jpg
python predict.py path\to\clip.mp4 --device cpu
```

Prediction renders go under `results/predictions/` and are ignored by Git. The backend processes uploads in memory or temporary system files and removes them after inference; it does not store uploaded media or evidence.

## Main source structure

```text
backend/                           FastAPI app, settings, schemas, model inference
frontend/                          Source browser UI: HTML, CSS, and JavaScript
model/
  roadwatch-yolo.onnx              Browser inference model
  weights/best.pt                  Fine-tuned YOLO checkpoint
  classes.yaml                     Model class order
scripts/                           Data conversion, training, and evaluation source
predict.py                         Image/video CLI using the included checkpoint
serve.py                           Static development server for the source frontend
requirements.txt                   Python backend, training, and CLI dependencies
.env.example                       Safe local backend configuration defaults
results/model-evaluation.md        Held-out evaluation report
outputs/traffic-watch/             Standalone release/demo and release tooling
outputs/roadwatch-website.zip      Downloadable standalone demo
```

There is no database or persistent upload/evidence subsystem. Backend uploads are temporary. The files under `outputs/traffic-watch/` are the packaged demo and release tools; the main app source is in the top-level `backend/`, `frontend/`, `model/`, and `scripts/` directories.

## Model and evaluation

The included YOLO11n model was fine-tuned for 8 epochs on 4,644 training images at 512px and batch size 8 on CPU. Training validation used 117 images. The separate held-out test set has 78 images and 497 labeled instances. Current results are mAP@50 **0.884** and mAP@50–95 **0.472**. See [`results/model-evaluation.md`](results/model-evaluation.md) for class-level precision, recall, and AP.

Results are preliminary and describe this dataset and camera style. The detector can miss or miscount unseen examples. Helmet evidence may be occluded or associated with the wrong rider. Red-light crossing is not assessed. A missing alert does not establish compliance; review the original media.

## Backend configuration

`.env` is optional. `ROADWATCH_MODEL_PATH`, `ROADWATCH_DEVICE`, `ROADWATCH_IMAGE_MAX_MB`, `ROADWATCH_VIDEO_MAX_MB`, and `ROADWATCH_MAX_VIDEO_FRAMES` are documented in `.env.example`. The API binds to localhost by default and has no authentication; keep it private unless authentication and deployment-specific upload controls are added.

## Train and evaluate

The prepared YOLO-format dataset is included under `data/processed/yolo-data/`; image files are stored with Git LFS. Install Git LFS and run `git lfs pull` after cloning to fetch them. The source is **Traffic Rule Violation Detection Dataset in Dhaka Urban Traffic Environment, v1** from the [Mendeley Data record](https://doi.org/10.17632/ycv2mbph4b.1), by Ashesh Bar, Manobendra Biswas, Abir Hasan, Marufur Rahman Mithu, Faisal Ahmad, and Tonmoy Das, licensed CC BY-NC 4.0. The dataset and derived model are for non-commercial use unless separate permission is obtained. Preserve attribution when sharing; see [data/DATASET_AND_LIMITATIONS.md](data/DATASET_AND_LIMITATIONS.md).

The included `data/processed/yolo-data/traffic.yaml` is ready to use after `git lfs pull`. To regenerate it from the original COCO package, extract its `augmented_dataset` with `train`, `valid`, and `test` subfolders:

```powershell
python scripts/prepare_yolo_data.py --dataset-root "data/source/augmented_dataset" --output "data/processed/yolo-data"
python scripts/train_yolo.py --data "data/processed/yolo-data/traffic.yaml" --model yolo11n.pt --epochs 8 --imgsz 512 --batch 8 --device cpu --project runs --name roadwatch-yolo11n
python scripts/evaluate_export_yolo.py --weights "runs/roadwatch-yolo11n/weights/best.pt" --data "data/processed/yolo-data/traffic.yaml" --output model/roadwatch-yolo.onnx --report results/model-evaluation.md
```

Keep the 78-image test split out of training and checkpoint selection. For detailed data, license, evaluation, and website release instructions, see [`outputs/traffic-watch/training/README.md`](outputs/traffic-watch/training/README.md). When updating an evaluation report, also refresh the performance panel, standalone page, and ZIP from that report and matching validation history.

## Ignore and secret handling

`.gitignore` excludes `.env` files except `.env.example`, credentials, Python environments/caches, downloaded datasets, generated uploads/predictions/training output, raw video formats, and unrelated checkpoints. The included `model/weights/best.pt` is explicitly allowed; it is a 5.45 MB project checkpoint. Do not add API keys, passwords, tokens, private footage, or raw video. The prepared, attributed YOLO dataset is included with Git LFS.

