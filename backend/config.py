"""Environment-backed settings for the local RoadWatch API."""
from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]
load_dotenv(ROOT / ".env", override=False)


def _positive_int(name: str, default: int, maximum: int) -> int:
    raw = os.getenv(name, str(default))
    try:
        value = int(raw)
    except ValueError as exc:
        raise ValueError(f"{name} must be an integer") from exc
    if not 1 <= value <= maximum:
        raise ValueError(f"{name} must be between 1 and {maximum}")
    return value


@dataclass(frozen=True)
class Settings:
    model_path: Path
    device: str
    max_image_bytes: int
    max_video_bytes: int
    max_video_frames: int
    image_size: int = 512


def load_settings() -> Settings:
    model_path = Path(os.getenv("ROADWATCH_MODEL_PATH", "model/weights/best.pt"))
    if not model_path.is_absolute():
        model_path = ROOT / model_path
    return Settings(
        model_path=model_path.resolve(),
        device=os.getenv("ROADWATCH_DEVICE", "cpu").strip() or "cpu",
        max_image_bytes=_positive_int("ROADWATCH_IMAGE_MAX_MB", 20, 500) * 1024 * 1024,
        max_video_bytes=_positive_int("ROADWATCH_VIDEO_MAX_MB", 100, 2000) * 1024 * 1024,
        max_video_frames=_positive_int("ROADWATCH_MAX_VIDEO_FRAMES", 30, 120),
    )


settings = load_settings()
