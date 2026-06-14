"""
GroomX v6 - Simple file server that bypasses Flask/Jinja2 completely
Run this instead of app.py if you keep getting Jinja2 errors
"""
import http.server
import socketserver
import threading
import os

# Serve the HTML directly on port 8080
os.chdir(os.path.join(os.path.dirname(__file__), 'static'))

Handler = http.server.SimpleHTTPRequestHandler

print("="*50)
print("  GroomX Frontend: http://localhost:8080/groomx_v6.html")
print("="*50)

with socketserver.TCPServer(("", 8080), Handler) as httpd:
    httpd.serve_forever()