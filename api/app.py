"""Stdlib HTTP wrapper around the ViridisOS service (zero third-party deps).

Swap for FastAPI/uvicorn in production if desired (see HANDOFF_NOTES.md); the routing
logic lives in `service.dispatch`, so the transport is interchangeable.

Run:  python3 -m api.app        (serves on :8085 with the Mutualist module registered)
"""

from __future__ import annotations

import json
import sys
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from viridis_platform import build_platform
from api.service import ViridisOSService, dispatch


def build_service() -> ViridisOSService:
    # assemble the full catalog against the LIVE canon (published theorems → LIVE, pending → BLOCKED)
    registry, certifier = build_platform()
    return ViridisOSService(registry, certifier)


def make_handler(service: ViridisOSService):
    class Handler(BaseHTTPRequestHandler):
        def _respond(self, status: int, payload: dict):
            data = json.dumps(payload, default=str).encode("utf-8")
            self.send_response(status)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)

        def _body(self) -> dict:
            n = int(self.headers.get("Content-Length", 0) or 0)
            if not n:
                return {}
            return json.loads(self.rfile.read(n).decode("utf-8"))

        def do_GET(self):
            status, payload = dispatch(service, "GET", self.path, None)
            self._respond(status, payload)

        def do_POST(self):
            try:
                body = self._body()
            except json.JSONDecodeError:
                return self._respond(400, {"error": "invalid json"})
            status, payload = dispatch(service, "POST", self.path, body)
            self._respond(status, payload)

        def log_message(self, *args):  # quiet
            pass
    return Handler


def run(port: int = 8085):
    server = HTTPServer(("0.0.0.0", port), make_handler(build_service()))
    print(f"ViridisOS API on :{port}")
    server.serve_forever()


if __name__ == "__main__":
    run()
