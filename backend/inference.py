"""Load the RoadWatch checkpoint once and run serialized model inference."""
from __future__ import annotations

from pathlib import Path
from threading import Lock
from typing import Any

import numpy as np

CLASS_NAMES = (
    "motorcycle",
    "helmet_on",
    "no_helmet",
    "rider",
    "triple_riding",
)

# Match the class-specific cutoffs used by the browser demo.
CONFIDENCE_THRESHOLDS = {
    0: 0.10,
    1: 0.08,
    2: 0.55,
    3: 0.10,
    4: 0.35,
}
NOTICE = (
    "Preliminary model detections only. Counts are boxes, not unique people or vehicles. "
    "The model may miss or miscount unseen examples; review the original media."
)


class RoadWatchInference:
    def __init__(self, model_path: Path, device: str, image_size: int = 512) -> None:
        self.model_path = model_path
        self.device = device
        self.image_size = image_size
        self._model: Any | None = None
        self._lock = Lock()

    @property
    def loaded(self) -> bool:
        return self._model is not None

    def load(self) -> None:
        if not self.model_path.is_file():
            raise FileNotFoundError(f"RoadWatch checkpoint not found: {self.model_path}")
        from ultralytics import YOLO

        self._model = YOLO(str(self.model_path))
        names = self._model.names
        normalized = tuple(names[i] for i in range(len(names)))
        if normalized != CLASS_NAMES:
            raise ValueError(
                "Checkpoint class order does not match model/classes.yaml: "
                f"{normalized!r}"
            )

    def predict_frame(self, image: np.ndarray) -> dict[str, Any]:
        if self._model is None:
            raise RuntimeError("The RoadWatch model has not loaded")

        with self._lock:
            result = self._model.predict(
                source=image,
                imgsz=self.image_size,
                conf=min(CONFIDENCE_THRESHOLDS.values()),
                device=self.device,
                verbose=False,
            )[0]

        height, width = image.shape[:2]
        detections: list[dict[str, Any]] = []
        counts = {name: 0 for name in CLASS_NAMES}
        boxes = result.boxes
        if boxes is not None:
            for box in boxes:
                class_id = int(box.cls[0].item())
                if not 0 <= class_id < len(CLASS_NAMES):
                    continue
                confidence = float(box.conf[0].item())
                if confidence < CONFIDENCE_THRESHOLDS[class_id]:
                    continue
                coordinates = tuple(round(float(x), 2) for x in box.xyxy[0].tolist())
                class_name = CLASS_NAMES[class_id]
                counts[class_name] += 1
                detections.append(
                    {
                        "class_name": class_name,
                        "class_id": class_id,
                        "confidence": round(confidence, 4),
                        "box_xyxy": coordinates,
                    }
                )

        return {
            "width": int(width),
            "height": int(height),
            "detection_count": len(detections),
            "counts": counts,
            "detections": detections,
        }
