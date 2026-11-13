"""
Server Launcher for GigBid Full-Stack Web Application
Runs:
1. Frontend Web Interface on http://localhost:5173
2. FastAPI Backend on http://localhost:8000
3. GigSim Marketplace Simulator on http://localhost:8001
"""

import asyncio
import http.server
import socketserver
import sys
import threading
import uvicorn
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from apps.api.main import app as fastapi_app
from gigsim.server import app as gigsim_app

WEB_DIR = Path("apps/web").resolve()

class WebHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(WEB_DIR), **kwargs)

    def do_GET(self):
        # SPA fallback to index.html
        path = self.translate_path(self.path)
        if not Path(path).exists() or Path(path).is_dir():
            self.path = "/index.html"
        return super().do_GET()

def start_frontend():
    port = 5173
    handler = WebHandler
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(("0.0.0.0", port), handler) as httpd:
        print(f"[UI] Web Interface running at http://localhost:{port}")
        httpd.serve_forever()

def start_gigsim():
    uvicorn.run(gigsim_app, host="0.0.0.0", port=8001, log_level="warning")

def start_backend():
    uvicorn.run(fastapi_app, host="0.0.0.0", port=8000, log_level="info")

if __name__ == "__main__":
    t_ui = threading.Thread(target=start_frontend, daemon=True)
    t_ui.start()

    t_sim = threading.Thread(target=start_gigsim, daemon=True)
    t_sim.start()

    print("[API] Starting FastAPI Backend on http://localhost:8000")
    start_backend()
