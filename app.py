import http.server
import socketserver
import json
import build_all
import os
import threading

PORT = 5000
DIRECTORY = os.path.dirname(os.path.abspath(__file__))

class DashboardHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)

    def do_POST(self):
        if self.path == '/api/update':
            print("Received update request...")
            success = build_all.run_full_build()
            
            self.send_response(200 if success else 500)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            
            response = {"success": success, "message": "Update successful" if success else "Update failed"}
            self.wfile.write(json.dumps(response).encode('utf-8'))
        else:
            self.send_error(404, "File not found")

    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        super().end_headers()

def run_server():
    with socketserver.TCPServer(("", PORT), DashboardHandler) as httpd:
        print(f"Serving ICT Dashboard at http://localhost:{PORT}")
        print("Press Ctrl+C to stop.")
        httpd.serve_forever()

if __name__ == "__main__":
    run_server()
