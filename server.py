"""
HTTP Server for Travel Recommendation System

Provides REST API endpoints for travel spot recommendations.
Serves the web frontend and handles all API requests.

Author: Travel Recommendation Team
Version: 2.0
"""
import json
import os
import sys
import logging
from http.server import HTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
from typing import Dict, Any, Optional, Tuple

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s: %(message)s'
)
logger = logging.getLogger(__name__)

# Add parent directory to path to import src modules
sys.path.insert(0, str(Path(__file__).parent))

from src.recommendation_system import TravelSpotRecommendationSystem


class APIRequestHandler(SimpleHTTPRequestHandler):
    """
    HTTP Request Handler for API and static files
    
    Handles:
    - GET requests for API endpoints and static files
    - POST requests for recommendations and adding places
    - DELETE requests for removing places
    - OPTIONS requests for CORS preflight
    """
    
    def __init__(self, *args, **kwargs):
        """Initialize handler with web directory"""
        super().__init__(*args, directory=str(Path(__file__).parent / 'web'), **kwargs)
    
    def end_headers(self):
        """Add CORS headers to all responses"""
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, DELETE, OPTIONS')
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
    
    def do_DELETE(self):
        """Handle DELETE requests"""
        self.send_error(404)
    
    def handle_recommend(self):
        """
        Handle recommendation request.
        
        Expected JSON:
        {
            "query": "string",
            "top_k": int (optional, default 5)
        }
        
        Returns:
        {
            "success": bool,
            "query": str,
            "recommendations": list,
            "total_results": int,
            "parsed_constraints": dict
        }
        """
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            if content_length == 0:
                return self.send_error_response(400, "Request body is empty")
                
            body = self.rfile.read(content_length).decode('utf-8')
            data = json.loads(body)
            
            query = data.get('query', '').strip()
            top_k = data.get('top_k', 5)
            
            if not query:
                return self.send_error_response(400, "Query is required and cannot be empty")
            
            if not isinstance(top_k, int) or top_k < 1:
                return self.send_error_response(400, "top_k must be a positive integer")
            
            if top_k > 100:  # Reasonable upper limit
                return self.send_error_response(400, "top_k cannot exceed 100")
            
            # Get recommendations from system
            result = recommendation_system.recommend_with_explanation(query, top_k=top_k)
            
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            
            response = {
                'success': True,
                'query': query,
                'recommendations': result['recommendations'],
                'total_results': result['total_results'],
                'parsed_constraints': result['parsed_constraints']
            }
            
            self.wfile.write(json.dumps(response).encode('utf-8'))
            logger.info(f"Recommendation request: query='{query}', top_k={top_k}, results={result['total_results']}")
            
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in request: {str(e)}")
            self.send_error_response(400, "Invalid JSON in request body")
        except ValueError as e:
            logger.error(f"Value error in recommendation: {str(e)}")
            self.send_error_response(400, f"Invalid input: {str(e)}")
        except Exception as e:
            logger.error(f"Error in recommendation: {str(e)}", exc_info=True)
            self.send_error_response(500, f"Recommendation error: {str(e)}")
    
    def handle_all_spots(self):
        """
        Handle request for all destinations.
        
        Returns: List of all travel spots with metadata
        """
        try:
            spots = recommendation_system.get_all_spots()
            
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            
            response = {
                'success': True,
                'spots': spots,
                'total_spots': len(spots)
            }
            
            self.wfile.write(json.dumps(response).encode('utf-8'))
            logger.info(f"All spots request: returned {len(spots)} spots")
            
        except Exception as e:
            logger.error(f"Error retrieving spots: {str(e)}")
            self.send_error_response(500, f"Error retrieving spots: {str(e)}")
    
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
    
    def send_error_response(self, code: int, message: str) -> None:
        """
        Send a JSON error response.
        
        Args:
            code: HTTP status code
            message: Error message
            
        Raises:
            ValueError: If code is not a valid HTTP status code
        """
        if not 100 <= code < 600:
            raise ValueError(f"Invalid HTTP status code: {code}")
            
        self.send_response(code)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        
        response = {
            'success': False,
            'error': message,
            'code': code
        }
        
        self.wfile.write(json.dumps(response).encode('utf-8'))
        logger.warning(f"Error response: {code} - {message}")
    
    @staticmethod
    def _get_dataset_path() -> str:
        """Get the path to the dataset file"""
        return os.path.join(os.path.dirname(__file__), 'data', 'travel_spots.json')
    
    def log_message(self, format: str, *args) -> None:
        """Log request information with timestamp"""
        logger.info(f"[{self.client_address[0]}] {format % args}")


# Initialize recommendation system globally
def setup_recommendation_system() -> TravelSpotRecommendationSystem:
    """
    Setup and initialize the recommendation system.
    
    Returns:
        Initialized TravelSpotRecommendationSystem instance
    """
    dataset_path = os.path.join(os.path.dirname(__file__), 'data', 'travel_spots.json')
    system = TravelSpotRecommendationSystem(dataset_path)
    logger.info("Recommendation system initialized successfully")
    return system


def main():
    """Main entry point for the server"""
    try:
        # Setup recommendation system
        global recommendation_system
        recommendation_system = setup_recommendation_system()
        
        # Start server
        PORT = 8001
        server_address = ('', PORT)
        httpd = HTTPServer(server_address, APIRequestHandler)
        
        logger.info("=" * 60)
        logger.info("Travel Recommendation System - Backend Server")
        logger.info("=" * 60)
        logger.info(f"Server running on http://localhost:{PORT}")
        logger.info(f"Web Interface: http://localhost:{PORT}/index.html")
        logger.info("")
        logger.info("API Endpoints:")
        logger.info("  POST   /api/recommend        - Get recommendations")
        logger.info("  GET    /api/all-spots        - Get all destinations")
        logger.info("  GET    /api/health           - Health check")
        logger.info("")
        logger.info("Press CTRL+C to stop the server")
        logger.info("=" * 60)
        
        httpd.serve_forever()
        
    except KeyboardInterrupt:
        logger.info("\n✅ Server stopped by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Server error: {str(e)}", exc_info=True)
        sys.exit(1)


if __name__ == '__main__':
    main()
