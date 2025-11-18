"""
Simple HTTP Server for Travel Recommendation System
Serves the web frontend and provides API endpoints
"""
import json
import os
from http.server import HTTPServer, SimpleHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import sys
from pathlib import Path

# Add parent directory to path to import src modules
sys.path.insert(0, str(Path(__file__).parent))

from src.recommendation_system import TravelSpotRecommendationSystem


class APIRequestHandler(SimpleHTTPRequestHandler):
    """Custom request handler for API and static files"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(Path(__file__).parent / 'web'), **kwargs)
    
    def end_headers(self):
        """Add CORS headers to responses"""
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        super().end_headers()
    
    def do_OPTIONS(self):
        """Handle CORS preflight requests"""
        self.send_response(200)
        self.end_headers()
    
    def do_POST(self):
        """Handle POST requests for API"""
        if self.path == '/api/recommend':
            self.handle_recommend()
        else:
            self.send_error(404)
    
    def do_GET(self):
        """Handle GET requests"""
        if self.path == '/api/all-spots':
            self.handle_all_spots()
        elif self.path == '/api/health':
            self.handle_health()
        else:
            # Serve static files
            super().do_GET()
    
    def handle_recommend(self):
        """Handle recommendation request"""
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length).decode('utf-8')
            data = json.loads(body)
            
            query = data.get('query', '')
            top_k = data.get('top_k', 5)
            
            if not query:
                self.send_error_response(400, "Query is required")
                return
            
            # Get recommendations from system
            result = recommendation_system.recommend_with_explanation(query, top_k=top_k)
            
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            
            response = {
                'query': query,
                'recommendations': result['recommendations'],
                'total_results': result['total_results'],
                'parsed_constraints': result['parsed_constraints']
            }
            
            self.wfile.write(json.dumps(response).encode('utf-8'))
            
        except Exception as e:
            self.send_error_response(500, str(e))
    
    def handle_all_spots(self):
        """Handle request for all destinations"""
        try:
            spots = recommendation_system.get_all_spots()
            
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            
            response = {
                'spots': spots,
                'total_spots': len(spots)
            }
            
            self.wfile.write(json.dumps(response).encode('utf-8'))
            
        except Exception as e:
            self.send_error_response(500, str(e))
    
    def handle_health(self):
        """Health check endpoint"""
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        
        response = {
            'status': 'healthy',
            'service': 'Travel Recommendation API'
        }
        
        self.wfile.write(json.dumps(response).encode('utf-8'))
    
    def send_error_response(self, code, message):
        """Send error response"""
        self.send_response(code)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        
        response = {
            'error': message,
            'code': code
        }
        
        self.wfile.write(json.dumps(response).encode('utf-8'))
    
    def log_message(self, format, *args):
        """Log request information"""
        print(f"[{self.client_address[0]}] {format % args}")


# Initialize recommendation system globally
def setup_recommendation_system():
    """Setup the recommendation system"""
    dataset_path = os.path.join(os.path.dirname(__file__), 'data', 'travel_spots.json')
    return TravelSpotRecommendationSystem(dataset_path)


if __name__ == '__main__':
    # Setup recommendation system
    recommendation_system = setup_recommendation_system()
    
    # Start server
    PORT = 8000
    server_address = ('', PORT)
    httpd = HTTPServer(server_address, APIRequestHandler)
    
    print(f"""
    ╔═══════════════════════════════════════════════════════════╗
    ║   Travel Recommendation System - Backend Server           ║
    ╚═══════════════════════════════════════════════════════════╝
    
    🚀 Server running on http://localhost:{PORT}
    🌐 Web Interface: http://localhost:{PORT}/index.html
    
    📡 API Endpoints:
       POST /api/recommend - Get recommendations
       GET  /api/all-spots - Get all destinations
       GET  /api/health   - Health check
    
    Press CTRL+C to stop the server
    """)
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n✅ Server stopped")
