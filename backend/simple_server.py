"""
Simple HTTP server using Python standard library only
No external dependencies required
Designer: Abdullah Alawiss
"""

import http.server
import socketserver
import os
import json
from urllib.parse import urlparse

PORT = int(os.environ.get('PORT', 8000))

class AICallcenterHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        # Parse the URL path
        parsed_path = urlparse(self.path)
        path = parsed_path.path
        
        # Health check endpoint
        if path == '/health':
            self.send_json_response({
                "status": "healthy",
                "service": "ai-callcenter-backend",
                "version": "1.0.0",
                "designer": "Abdullah Alawiss"
            })
        
        # API test endpoint
        elif path == '/api/v1/test':
            self.send_json_response({
                "message": "API endpoint working",
                "framework": "Python Standard Library",
                "python_version": "3.11",
                "designer": "Abdullah Alawiss"
            })
        
        # Root endpoint
        elif path == '/' or path == '':
            self.send_json_response({
                "message": "AI Callcenter Agent MVP",
                "status": "running",
                "endpoints": [
                    "/health",
                    "/api/v1/test"
                ],
                "designer": "Abdullah Alawiss"
            })
        
        # 404 for other paths
        else:
            self.send_json_response({
                "error": "Not Found",
                "path": path,
                "designer": "Abdullah Alawiss"
            }, status=404)
    
    def send_json_response(self, data, status=200):
        """Send JSON response with proper headers"""
        self.send_response(status)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        response = json.dumps(data, ensure_ascii=False, indent=2)
        self.wfile.write(response.encode('utf-8'))
    
    def log_message(self, format, *args):
        """Custom log message format"""
        print(f"[{self.log_date_time_string()}] {format % args}")

def start_server():
    """Start the HTTP server"""
    try:
        with socketserver.TCPServer(("", PORT), AICallcenterHandler) as httpd:
            print(f"🚀 AI Callcenter Server starting on port {PORT}")
            print(f"📍 Health check: http://localhost:{PORT}/health")
            print(f"🧪 API test: http://localhost:{PORT}/api/v1/test")
            print(f"👨‍💻 Designer: Abdullah Alawiss")
            httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
    except Exception as e:
        print(f"❌ Server error: {e}")

if __name__ == '__main__':
    start_server()
