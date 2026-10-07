"""Serve the self-contained Roadwatch demo from localhost (Python standard library only)."""
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import os
import threading
import webbrowser

ROOT = Path(__file__).resolve().parent
PORT = 8765


class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(ROOT), **kwargs)

    def end_headers(self):
        self.send_header("Cache-Control", "no-store")
        super().end_headers()


if __name__ == "__main__":
    os.chdir(ROOT)
    try:
        server = ThreadingHTTPServer(("127.0.0.1", PORT), Handler)
    except OSError:
        # If another application already owns the usual demo port, let Windows
        # choose an available local port and use that URL for this session.
        server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    host, port = server.server_address[:2]
    url = f"http://{host}:{port}/index.html"

    # Bind/listen above, then start the request loop before launching Chrome.
    # Opening the browser before this point can race server startup.
    worker = threading.Thread(target=server.serve_forever, daemon=True)
    worker.start()
    print(f"Roadwatch is ready at {url}\nKeep this window open while using it. Press Ctrl+C to stop.", flush=True)
    if os.environ.get("ROADWATCH_NO_OPEN") != "1":
        webbrowser.open(url)
    worker.join()
