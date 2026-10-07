"""Inline the current YOLO model and app code so index.html works as a local file."""
from __future__ import annotations

import argparse
import base64
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=ROOT, help="traffic-watch folder")
    args = parser.parse_args()
    root = args.root.resolve()
    model_path = root / "roadwatch-yolo.onnx"
    sample_video_path = root / "sample-roadwatch-demo.webm"
    app_path = root / "app.js"
    index_path = root / "index.html"

    model_b64 = base64.b64encode(model_path.read_bytes()).decode("ascii")
    model_script = (
        "<script>window.roadwatchModelBytes = Uint8Array.from(atob('"
        + model_b64
        + "'), c => c.charCodeAt(0));</script>"
    )
    sample_video_b64 = base64.b64encode(sample_video_path.read_bytes()).decode("ascii")
    sample_video_script = (
        "<script>window.roadwatchSampleVideoData = 'data:video/webm;base64,"
        + sample_video_b64
        + "';</script>"
    )
    app_script = "<script>" + app_path.read_text(encoding="utf-8") + "</script>"
    html = index_path.read_text(encoding="utf-8")

    html, model_count = re.subn(
        r"<script>window\.roadwatchModelBytes\s*=.*?</script>",
        lambda _: model_script,
        html,
        count=1,
        flags=re.DOTALL,
    )
    if model_count != 1:
        raise RuntimeError("Could not find the inlined YOLO model block in index.html")
    html, video_count = re.subn(
        r"<script>window\.roadwatchSampleVideoData\s*=.*?</script>",
        lambda _: sample_video_script,
        html,
        count=1,
        flags=re.DOTALL,
    )
    if video_count != 1:
        raise RuntimeError("Could not find the sample video data block in index.html")
    html, app_count = re.subn(
        r"<script>const MODEL_URL\s*=.*?</script>",
        lambda _: app_script,
        html,
        count=1,
        flags=re.DOTALL,
    )
    if app_count != 1:
        raise RuntimeError("Could not find the inlined app code block in index.html")

    index_path.write_text(html, encoding="utf-8")
    (root / "roadwatch-model.js").write_text(model_script[8:-9] + "\n", encoding="ascii")
    print(f"Updated standalone browser demo: {index_path}")


if __name__ == "__main__":
    main()
