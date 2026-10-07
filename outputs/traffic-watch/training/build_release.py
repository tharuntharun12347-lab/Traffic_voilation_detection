"""Create the shareable ZIP with a single-file, local-browser-friendly demo page."""
from __future__ import annotations

from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile


ROOT = Path(__file__).resolve().parents[1]
DESTINATION = ROOT.parent / "roadwatch-website.zip"
OMIT = {"app.js", "roadwatch-model.js", "roadwatch-yolo.onnx", "sample-roadwatch-demo.webm"}


def main() -> None:
    with ZipFile(DESTINATION, "w", compression=ZIP_DEFLATED, compresslevel=9) as archive:
        for path in sorted(ROOT.rglob("*")):
            if not path.is_file() or "__pycache__" in path.parts:
                continue
            if path.name in OMIT:
                continue
            archive.write(path, Path("traffic-watch") / path.relative_to(ROOT))
    print(f"Built {DESTINATION}")


if __name__ == "__main__":
    main()
