# RoadWatch backend

FastAPI serves the source frontend and provides local model inference. It loads `model/weights/best.pt` once on startup, applies the same class confidence cutoffs as the browser demo, and returns JSON box detections.

## Start

From the repository root, after installing `requirements.txt`:

```powershell
Copy-Item .env.example .env
python -m uvicorn backend.main:app --reload --host 127.0.0.1 --port 8000
```

Open the frontend at `http://127.0.0.1:8000/` and interactive API docs at `http://127.0.0.1:8000/docs`. The existing frontend continues using its browser ONNX model; the new API is available to other clients and future integrations.

## Endpoints

- `GET /api/health` — model load status and device.
- `GET /api/model` — classes, input size, thresholds, and upload policy.
- `POST /api/predict/image` — multipart `file`: JPG, PNG, WEBP, or BMP.
- `POST /api/predict/video` — multipart `file`: MP4, MOV, AVI, MKV, or WEBM; samples up to the configured frame count.

Example image request:

```powershell
curl.exe -F "file=@photo.jpg" http://127.0.0.1:8000/api/predict/image
```

Video responses include detections and timestamps per sampled frame. Aggregate totals count boxes across sampled frames, not unique people, vehicles, or events.

## Upload handling and limits

Uploads are decoded in memory or a temporary system file and removed after inference. The API does not persist uploads or evidence. Limits are configured by `ROADWATCH_IMAGE_MAX_MB`, `ROADWATCH_VIDEO_MAX_MB`, and `ROADWATCH_MAX_VIDEO_FRAMES`; the model and device use `ROADWATCH_MODEL_PATH` and `ROADWATCH_DEVICE`. `.env` is optional and ignored by Git.

This service binds to localhost by default. It has no authentication and is intended for local development; do not expose it to an untrusted network without adding authentication, rate limits, and deployment-specific upload controls. Results are preliminary and require human review. Red-light crossing is not assessed.
