import os
import signal
import subprocess
import sys
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

PORT = int(os.getenv("PORT", "10000"))

bot_process = subprocess.Popen([sys.executable, "main.py"])

class HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path.rstrip("/") == "/health":
            alive = bot_process.poll() is None
            body = b'{"status":"ok"}' if alive else b'{"status":"down"}'
            self.send_response(200 if alive else 503)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return

        body = b"MusRemixBot is running"
        self.send_response(200)
        self.send_header("Content-Type", "text/plain; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format, *args):
        return

def shutdown(signum, frame):
    if bot_process.poll() is None:
        bot_process.terminate()
        try:
            bot_process.wait(timeout=10)
        except subprocess.TimeoutExpired:
            bot_process.kill()
    raise SystemExit(0)

signal.signal(signal.SIGTERM, shutdown)
signal.signal(signal.SIGINT, shutdown)

server = HTTPServer(("0.0.0.0", PORT), HealthHandler)

def serve():
    server.serve_forever()

threading.Thread(target=serve, daemon=True).start()

# If the unchanged bot exits, stop the container so Render can restart it.
exit_code = bot_process.wait()
server.shutdown()
sys.exit(exit_code)
