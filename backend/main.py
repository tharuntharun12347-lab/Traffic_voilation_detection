"""FastAPI application for RoadWatch image and sampled-video inference."""
from __future__ import annotations

import tempfile
from contextlib import asynccontextmanager
from pathlib import Path
from typing import AsyncIterator

import cv2
import numpy as np
from fastapi import Depends, FastAPI, File, HTTPException, Request, UploadFile
from fastapi.responses import FileResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles

from backend.config import ROOT, settings
from backend.inference import CLASS_NAMES, CONFIDENCE_THRESHOLDS, NOTICE, RoadWatchInference
from backend.schemas import ImagePrediction, ModelInfo, VideoFramePrediction, VideoPrediction

IMAGE_SUFFIXES = {".jpg", ".jpeg", ".png", ".webp", ".bmp"}
VIDEO_SUFFIXES = {".mp4", ".mov", ".avi", ".mkv", ".webm"}
SAMPLE_VIDEO = ROOT / "outputs" / "traffic-watch" / "sample-roadwatch-demo.webm"
ONNX_MODEL = ROOT / "model" / "roadwatch-yolo.onnx"


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    inference = RoadWatchInference(
        model_path=settings.model_path,
        device=settings.device,
        image_size=settings.image_size,
    )
    inference.load()
    app.state.inference = inference
    yield


app = FastAPI(
    title="RoadWatch AI API",
    description=(
        "Local image and sampled-video inference for the RoadWatch classroom demo. "
        "Detections are preliminary and require human review."
    ),
    version="1.0.0",
    lifespan=lifespan,
)


def get_inference(request: Request) -> RoadWatchInference:
    return request.app.state.inference


def _safe_filename(upload: UploadFile) -> str:
    return Path(upload.filename or "upload").name


@app.get("/", include_in_schema=False)
def home() -> RedirectResponse:
    return RedirectResponse(url="/frontend/", status_code=307)


@app.get("/api/health")
def health(inference: RoadWatchInference = Depends(get_inference)) -> dict[str, object]:
    return {
        "status": "ok" if inference.loaded else "loading",
        "model_loaded": inference.loaded,
        "device": settings.device,
    }


@app.get("/api/model", response_model=ModelInfo)
def model_info(inference: RoadWatchInference = Depends(get_inference)) -> ModelInfo:
    return ModelInfo(
        name="RoadWatch YOLO11n",
        classes=list(CLASS_NAMES),
        image_size=settings.image_size,
        device=settings.device,
        confidence_thresholds={
            CLASS_NAMES[class_id]: threshold
            for class_id, threshold in CONFIDENCE_THRESHOLDS.items()
        },
        upload_policy=(
            f"Uploads are processed temporarily; images up to {settings.max_image_bytes // (1024 * 1024)} MB, "
            f"videos up to {settings.max_video_bytes // (1024 * 1024)} MB and "
            f"{settings.max_video_frames} sampled frames. Files are not retained."
        ),
    )


@app.post("/api/predict/image", response_model=ImagePrediction)
def predict_image(
    file: UploadFile = File(...),
    inference: RoadWatchInference = Depends(get_inference),
) -> ImagePrediction:
    suffix = Path(file.filename or "").suffix.lower()
    if suffix not in IMAGE_SUFFIXES:
        raise HTTPException(status_code=415, detail="Upload a JPG, PNG, WEBP, or BMP image.")
    contents = file.file.read(settings.max_image_bytes + 1)
    if len(contents) > settings.max_image_bytes:
        raise HTTPException(status_code=413, detail="Image exceeds the configured upload limit.")
    image = cv2.imdecode(np.frombuffer(contents, dtype=np.uint8), cv2.IMREAD_COLOR)
    if image is None:
        raise HTTPException(status_code=422, detail="The uploaded file could not be decoded as an image.")
    try:
        result = inference.predict_frame(image)
    except Exception as exc:
        raise HTTPException(status_code=500, detail="Image inference failed.") from exc
    return ImagePrediction(filename=_safe_filename(file), notice=NOTICE, **result)


def _sample_indices(frame_count: int, limit: int) -> list[int]:
    count = min(frame_count, limit)
    if count <= 1:
        return [0]
    return sorted({round(i * (frame_count - 1) / (count - 1)) for i in range(count)})


@app.post("/api/predict/video", response_model=VideoPrediction)
def predict_video(
    file: UploadFile = File(...),
    inference: RoadWatchInference = Depends(get_inference),
) -> VideoPrediction:
    suffix = Path(file.filename or "").suffix.lower()
    if suffix not in VIDEO_SUFFIXES:
        raise HTTPException(status_code=415, detail="Upload an MP4, MOV, AVI, MKV, or WEBM video.")

    temporary_path: Path | None = None
    capture: cv2.VideoCapture | None = None
    try:
        with tempfile.NamedTemporaryFile(prefix="roadwatch-", suffix=suffix, delete=False) as temp:
            temporary_path = Path(temp.name)
            total = 0
            while True:
                chunk = file.file.read(1024 * 1024)
                if not chunk:
                    break
                total += len(chunk)
                if total > settings.max_video_bytes:
                    raise HTTPException(status_code=413, detail="Video exceeds the configured upload limit.")
                temp.write(chunk)

        capture = cv2.VideoCapture(str(temporary_path))
        if not capture.isOpened():
            raise HTTPException(status_code=422, detail="The uploaded file could not be opened as a video.")
        frame_count = int(capture.get(cv2.CAP_PROP_FRAME_COUNT))
        fps = float(capture.get(cv2.CAP_PROP_FPS))
        if frame_count <= 0:
            raise HTTPException(status_code=422, detail="The video contains no readable frames.")

        frames: list[VideoFramePrediction] = []
        aggregate = {name: 0 for name in CLASS_NAMES}
        for index in _sample_indices(frame_count, settings.max_video_frames):
            capture.set(cv2.CAP_PROP_POS_FRAMES, index)
            ok, frame = capture.read()
            if not ok or frame is None:
                continue
            result = inference.predict_frame(frame)
            frames.append(
                VideoFramePrediction(
                    frame_index=index,
                    timestamp_seconds=round(index / fps, 3) if fps > 0 else 0.0,
                    **result,
                )
            )
            for name, count in result["counts"].items():
                aggregate[name] += count
        if not frames:
            raise HTTPException(status_code=422, detail="No video frames could be decoded.")
        return VideoPrediction(
            filename=_safe_filename(file),
            source_frame_count=frame_count,
            sampled_frame_count=len(frames),
            frames=frames,
            detections_per_class_across_sampled_frames=aggregate,
            notice=(
                NOTICE
                + " Video counts sum detections across sampled frames and do not represent unique objects or events."
            ),
        )
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail="Video inference failed.") from exc
    finally:
        if capture is not None:
            capture.release()
        if temporary_path is not None:
            temporary_path.unlink(missing_ok=True)


@app.get("/model/roadwatch-yolo.onnx", include_in_schema=False)
def browser_model() -> FileResponse:
    return FileResponse(ONNX_MODEL, media_type="application/octet-stream", filename=ONNX_MODEL.name)


@app.get("/outputs/traffic-watch/sample-roadwatch-demo.webm", include_in_schema=False)
def sample_video() -> FileResponse:
    return FileResponse(SAMPLE_VIDEO, media_type="video/webm", filename=SAMPLE_VIDEO.name)


app.mount("/frontend", StaticFiles(directory=ROOT / "frontend", html=True), name="frontend")
