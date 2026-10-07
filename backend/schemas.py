"""Stable JSON response shapes for RoadWatch inference endpoints."""
from __future__ import annotations

from pydantic import BaseModel, Field


class Detection(BaseModel):
    class_name: str
    class_id: int
    confidence: float = Field(ge=0, le=1)
    box_xyxy: tuple[float, float, float, float]


class ImagePrediction(BaseModel):
    filename: str
    width: int
    height: int
    detection_count: int
    counts: dict[str, int]
    detections: list[Detection]
    notice: str


class VideoFramePrediction(BaseModel):
    frame_index: int
    timestamp_seconds: float
    width: int
    height: int
    detection_count: int
    counts: dict[str, int]
    detections: list[Detection]


class VideoPrediction(BaseModel):
    filename: str
    source_frame_count: int
    sampled_frame_count: int
    frames: list[VideoFramePrediction]
    detections_per_class_across_sampled_frames: dict[str, int]
    notice: str


class ModelInfo(BaseModel):
    name: str
    classes: list[str]
    image_size: int
    device: str
    confidence_thresholds: dict[str, float]
    upload_policy: str
