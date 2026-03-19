import http.server
import socketserver
import json
import build_all_ft1
import os

PORT = 5001
DIRECTORY = os.path.dirname(os.path.abspath(__file__))

class ThreadedHTTPServer(socketserver.ThreadingMixIn, http.server.HTTPServer):
    daemon_threads = True

class FT1DashboardHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)

    def do_POST(self):
        if self.path == '/api/update':
            print("\n[API] Received FT1 update request...")
            success = build_all_ft1.run_full_build()
            
            self.send_response(200 if success else 500)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            response = {"success": success, "message": "Update successful" if success else "Update failed"}
            self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))
            print("[API] FT1 Update request completed.\n")
        else:
            self.send_error(404, "File not found")

    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        super().end_headers()

def run_server():
    with ThreadedHTTPServer(("", PORT), FT1DashboardHandler) as httpd:
        print(f"Serving FT1 Dashboard at http://localhost:{PORT}")
        print("Threaded server enabled. Press Ctrl+C to stop.")
        httpd.serve_forever()

if __name__ == "__main__":
    run_server()
