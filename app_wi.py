import http.server
import socketserver
import json
import build_all_wi
import os

PORT = 5002
DIRECTORY = os.path.dirname(os.path.abspath(__file__))

class ThreadedHTTPServer(socketserver.ThreadingMixIn, http.server.HTTPServer):
    daemon_threads = True

class WIDashboardHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def do_POST(self):
        if self.path == '/api/update':
            print("\n[API] Received WI update request...")
            success = build_all_wi.run_full_build()

            body = json.dumps(
                {"success": success, "message": "Update successful" if success else "Update failed"},
                ensure_ascii=False
            ).encode('utf-8')

            self.send_response(200 if success else 500)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.send_header('Content-Length', str(len(body)))
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(body)
            self.wfile.flush()
            print("[API] WI Update request completed.\n")
        else:
            self.send_error(404, "Not Found")

    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        super().end_headers()

    def log_message(self, format, *args):
        print(f"[HTTP] {self.address_string()} - {format % args}")

def run_server():
    with ThreadedHTTPServer(("", PORT), WIDashboardHandler) as httpd:
        print(f"Serving WI Dashboard at http://localhost:{PORT}")
        print("Threaded server enabled. Press Ctrl+C to stop.")
        httpd.serve_forever()

if __name__ == "__main__":
    run_server()
