"""Serve the repository root so the frontend can load its model and sample assets."""
from __future__ import annotations

import argparse
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8000)
    args = parser.parse_args()
    handler = partial(SimpleHTTPRequestHandler, directory=str(ROOT))
    url = f"http://{args.host}:{args.port}/frontend/"
    print(f"RoadWatch source app: {url} (Ctrl+C to stop)")
    with ThreadingHTTPServer((args.host, args.port), handler) as server:
        server.serve_forever()


if __name__ == "__main__":
    main()
