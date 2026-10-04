"""Shared test helpers: paths and a tiny local HTTP server that plays ElevenLabs or the preview host."""
import json
import socket
import subprocess
import sys
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKILL = ROOT / "skills" / "prestige-voices"
SCRIPTS = SKILL / "scripts"
sys.path.insert(0, str(SCRIPTS))


class MockServer:
    """Serves one canned response per path prefix and records every request it gets."""

    def __init__(self, routes):
        # {path_prefix: (status, content_type, body_bytes[, extra_headers])}; status "hangup" closes the
        # connection after reading the request, without answering.
        self.routes = routes
        self.requests = []
        server = self

        class Handler(BaseHTTPRequestHandler):
            def _serve(self):
                length = int(self.headers.get("Content-Length") or 0)
                body = self.rfile.read(length) if length else b""
                server.requests.append({"method": self.command, "path": self.path,
                                        "headers": {k.lower(): v for k, v in self.headers.items()}, "body": body})
                for prefix, route in server.routes.items():
                    if self.path.startswith(prefix):
                        status, ctype, payload = route[:3]
                        if status == "hangup":
                            self.close_connection = True
                            return
                        self.send_response(status)
                        for name, value in (route[3] if len(route) > 3 else {}).items():
                            self.send_header(name, value)
                        self.send_header("Content-Type", ctype)
                        self.send_header("Content-Length", str(len(payload)))
                        self.end_headers()
                        if self.command != "HEAD":
                            self.wfile.write(payload)
                        return
                self.send_response(500)
                self.end_headers()

            do_GET = do_POST = do_HEAD = _serve

            def log_message(self, *args):
                pass

        self.httpd = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        self.url = f"http://127.0.0.1:{self.httpd.server_address[1]}"
        threading.Thread(target=self.httpd.serve_forever, daemon=True).start()

    def close(self):
        self.httpd.shutdown()
        self.httpd.server_close()


def json_body(status_text, message):
    return json.dumps({"detail": {"status": status_text, "message": message}}).encode()


def closed_port_url():
    s = socket.socket()
    s.bind(("127.0.0.1", 0))
    port = s.getsockname()[1]
    s.close()
    return f"http://127.0.0.1:{port}"


def run_script(name, *args, env=None, cwd=None):
    return subprocess.run([sys.executable, str(SCRIPTS / name), *args], capture_output=True, text=True,
                          encoding="utf-8", env=env, cwd=cwd, timeout=60)
