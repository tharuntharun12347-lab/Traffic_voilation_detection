# RoadWatch AI

RoadWatch is a classroom traffic-safety demo. The main application is a browser frontend that runs an ONNX YOLO11n model on uploaded photos or up to 30 sampled video frames. It displays motorcycles, riders, helmet evidence, and possible triple riding for human review. The repository also includes the trained checkpoint and the scripts used to prepare data, train, evaluate, and export the model.

## Run the source application

Use Python 3.12 and a modern browser. The web application loads ONNX Runtime Web from its CDN, so keep an internet connection available.

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python serve.py
```

Open the printed URL, normally [http://127.0.0.1:8000/frontend/](http://127.0.0.1:8000/frontend/). The source frontend is in `frontend/`; it loads `frontend/app.js`, the ONNX model from `model/`, and the sample clip in `outputs/traffic-watch/`. Uploaded media is processed in the browser and is not uploaded to a RoadWatch server.

For a quick command-line prediction on an image or video:

```powershell
python predict.py path	o\image.jpg
python predict.py path	o\clip.mp4 --device cpu
```

Predictions are written under `results/predictions/` and ignored by Git.

## Main source structure

```text
frontend/                         Source browser UI: HTML, CSS, and JavaScript
model/
  roadwatch-yolo.onnx             Browser inference model
  weights/best.pt                 Fine-tuned YOLO checkpoint
  classes.yaml                    Model class order
scripts/                          Data conversion, training, and evaluation source
predict.py                        Image/video CLI using the included checkpoint
serve.py                          Local development server for the source frontend
requirements.txt                  Python training and CLI dependencies
.env.example                      Documents that this browser-only app needs no secrets
results/model-evaluation.md       Held-out evaluation report
outputs/traffic-watch/            Standalone release/demo and release tooling
outputs/roadwatch-website.zip     Downloadable standalone demo
```

This project currently has no Python backend, database, persistent upload store, or server-side evidence system. The demo keeps uploads in the browser, so `backend/`, `database/`, `evidence/`, and persistent `uploads/` directories are not applicable and were not fabricated. The files in `outputs/traffic-watch/` are the packaged demo; they no longer stand in for the main source tree.

## Model and evaluation

The included YOLO11n model was fine-tuned for 8 epochs on 4,644 training images at 512px and batch size 8 on CPU. Training validation used 117 images. The separate held-out test set has 78 images and 497 labeled instances. Current results are mAP@50 **0.884** and mAP@50–95 **0.472**. See [`results/model-evaluation.md`](results/model-evaluation.md) for class-level precision, recall, and AP.

Results are preliminary and describe this dataset and camera style. The detector can miss or miscount unseen examples. Helmet evidence may be occluded or associated with the wrong rider. Red-light crossing is not assessed. A missing alert does not establish compliance; review the original media.

## Train and evaluate

The dataset is not included. Download **Traffic Rule Violation Detection Dataset in Dhaka Urban Traffic Environment, v1** from the [Mendeley Data record](https://doi.org/10.17632/ycv2mbph4b.1). It is by Ashesh Bar, Manobendra Biswas, Abir Hasan, Marufur Rahman Mithu, Faisal Ahmad, and Tonmoy Das and is licensed CC BY-NC 4.0. The dataset and derived model are for non-commercial use under the applicable license terms unless separate permission is obtained. Preserve attribution when sharing. Do not put source/converted images or annotations into Git.

After extracting the `augmented_dataset` with `train`, `valid`, and `test` subfolders:

```powershell
python scripts/prepare_yolo_data.py --dataset-root "data/source/augmented_dataset" --output "data/processed/yolo-data"
python scripts/train_yolo.py --data "data/processed/yolo-data/traffic.yaml" --model yolo11n.pt --epochs 8 --imgsz 512 --batch 8 --device cpu --project runs --name roadwatch-yolo11n
python scripts/evaluate_export_yolo.py --weights "runs/roadwatch-yolo11n/weights/best.pt" --data "data/processed/yolo-data/traffic.yaml" --output model/roadwatch-yolo.onnx --report results/model-evaluation.md
```

Keep the 78-image test split out of training and checkpoint selection. For detailed data, license, evaluation, and website release instructions, see [`outputs/traffic-watch/training/README.md`](outputs/traffic-watch/training/README.md). When updating an evaluation report, also refresh the performance panel, standalone page, and ZIP from that report and matching validation history.

## Ignore and secret handling

`.gitignore` excludes `.env` files except `.env.example`, credentials, Python environments/caches, downloaded datasets, uploads, generated prediction/training output, raw video formats, and unrelated checkpoints. The included `model/weights/best.pt` is explicitly allowed; it is a 5.45 MB project checkpoint. Do not add API keys, passwords, tokens, private footage, or dataset files.
