"""
Web Server for Destination Recommendation Engine

Delivers REST API endpoints for destination recommendations.
Hosts the web interface and processes all API calls.

Development Team: Destination Discovery Platform
Release: 2.0
"""
import json
import os
import sys
import logging
from http.server import HTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
from typing import Dict, Any, Optional, Tuple

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s: %(message)s'
)
logger = logging.getLogger(__name__)

# Include parent directory in path for src module imports
sys.path.insert(0, str(Path(__file__).parent))

from src.recommendation_system import TravelSpotRecommendationSystem


class APIRequestHandler(SimpleHTTPRequestHandler):
    """
    HTTP Request Handler for API calls and static content
    
    Processes:
    - GET requests for API endpoints and static resources
    - POST requests for recommendations and place additions
    - DELETE requests for place removals
    - OPTIONS requests for CORS preflight
    """
    
    def __init__(self, *args, **kwargs):
        """Set up handler with web directory"""
        super().__init__(*args, directory=str(Path(__file__).parent / 'web'), **kwargs)
    
    def end_headers(self):
        """Append CORS headers to all responses"""
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, DELETE, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        super().end_headers()
    
    def do_OPTIONS(self):
        """Process CORS preflight requests"""
        self.send_response(200)
        self.end_headers()
    
    def do_POST(self):
        """Process POST requests for API"""
        if self.path == '/api/recommend':
            self.process_recommendation_request()
        else:
            self.send_error(404)
    
    def do_GET(self):
        """Process GET requests"""
        if self.path == '/api/all-spots':
            self.process_all_spots_request()
        elif self.path == '/api/health':
            self.process_health_check()
        else:
            # Deliver static resources
            super().do_GET()
    
    def process_recommendation_request(self):
        """
        Process recommendation request.
        
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
            payload_size = int(self.headers.get('Content-Length', 0))
            if payload_size == 0:
                return self.deliver_error_response(400, "Request payload is missing")
                
            request_body = self.rfile.read(payload_size).decode('utf-8')
            request_data = json.loads(request_body)
            
            user_query = request_data.get('query', '').strip()
            result_count = request_data.get('top_k', 5)
            
            if not user_query:
                return self.deliver_error_response(400, "Query field is required and must not be empty")
            
            if not isinstance(result_count, int) or result_count < 1:
                return self.deliver_error_response(400, "top_k must be a positive integer")
            
            if result_count > 100:  # Reasonable upper bound
                return self.deliver_error_response(400, "top_k cannot exceed 100")
            
            # Fetch recommendations from engine
            recommendation_output = recommendation_engine.recommend_with_explanation(user_query, top_k=result_count)
            
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            
            api_response = {
                'success': True,
                'query': user_query,
                'recommendations': recommendation_output['recommendations'],
                'total_results': recommendation_output['total_results'],
                'parsed_constraints': recommendation_output['parsed_constraints']
            }
            
            self.wfile.write(json.dumps(api_response).encode('utf-8'))
            logger.info(f"Recommendation query: query='{user_query}', top_k={result_count}, results={recommendation_output['total_results']}")
            
        except json.JSONDecodeError as json_error:
            logger.error(f"Malformed JSON in request: {str(json_error)}")
            self.deliver_error_response(400, "Malformed JSON in request payload")
        except ValueError as value_error:
            logger.error(f"Value error in recommendation: {str(value_error)}")
            self.deliver_error_response(400, f"Invalid input: {str(value_error)}")
        except Exception as general_error:
            logger.error(f"Error in recommendation: {str(general_error)}", exc_info=True)
            self.deliver_error_response(500, f"Recommendation error: {str(general_error)}")
    
    def process_all_spots_request(self):
        """
        Process request for all destinations.
        
        Returns: List of all destinations with metadata
        """
        try:
            all_destinations = recommendation_engine.get_all_spots()
            
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            
            api_response = {
                'success': True,
                'spots': all_destinations,
                'total_spots': len(all_destinations)
            }
            
            self.wfile.write(json.dumps(api_response).encode('utf-8'))
            logger.info(f"All destinations request: returned {len(all_destinations)} destinations")
            
        except Exception as retrieval_error:
            logger.error(f"Error retrieving destinations: {str(retrieval_error)}")
            self.deliver_error_response(500, f"Error retrieving destinations: {str(retrieval_error)}")
    
    def process_health_check(self):
        """Health verification endpoint"""
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        
        health_response = {
            'status': 'healthy',
            'service': 'Travel Recommendation API'
        }
        
        self.wfile.write(json.dumps(health_response).encode('utf-8'))
    
    def deliver_error_response(self, status_code: int, error_message: str) -> None:
        """
        Deliver a JSON error response.
        
        Args:
            status_code: HTTP status code
            error_message: Error description
            
        Raises:
            ValueError: If status_code is not a valid HTTP code
        """
        if not 100 <= status_code < 600:
            raise ValueError(f"Invalid HTTP status code: {status_code}")
            
        self.send_response(status_code)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        
        error_response = {
            'success': False,
            'error': error_message,
            'code': status_code
        }
        
        self.wfile.write(json.dumps(error_response).encode('utf-8'))
        logger.warning(f"Error response: {status_code} - {error_message}")
    
    @staticmethod
    def _get_dataset_path() -> str:
        """Retrieve the path to the dataset file"""
        return os.path.join(os.path.dirname(__file__), 'data', 'travel_spots.json')
    
    def log_message(self, format: str, *args) -> None:
        """Log request information with timestamp"""
        logger.info(f"[{self.client_address[0]}] {format % args}")


# Set up recommendation engine globally
def initialize_recommendation_engine() -> TravelSpotRecommendationSystem:
    """
    Configure and initialize the recommendation engine.
    
    Returns:
        Initialized TravelSpotRecommendationSystem instance
    """
    data_file_path = os.path.join(os.path.dirname(__file__), 'data', 'travel_spots.json')
    engine = TravelSpotRecommendationSystem(data_file_path)
    logger.info("Recommendation engine initialized successfully")
    return engine


def main():
    """Main entry point for the server"""
    try:
        # Configure recommendation engine
        global recommendation_engine
        recommendation_engine = initialize_recommendation_engine()
        
        # Launch server
        SERVER_PORT = 8001
        server_bind_address = ('', SERVER_PORT)
        http_server = HTTPServer(server_bind_address, APIRequestHandler)
        
        logger.info("=" * 60)
        logger.info("Travel Recommendation System - Backend Server")
        logger.info("=" * 60)
        logger.info(f"Server running on http://localhost:{SERVER_PORT}")
        logger.info(f"Web Interface: http://localhost:{SERVER_PORT}/index.html")
        logger.info("")
        logger.info("API Endpoints:")
        logger.info("  POST   /api/recommend        - Get recommendations")
        logger.info("  GET    /api/all-spots        - Get all destinations")
        logger.info("  GET    /api/health           - Health check")
        logger.info("")
        logger.info("Press CTRL+C to stop the server")
        logger.info("=" * 60)
        
        http_server.serve_forever()
        
    except KeyboardInterrupt:
        logger.info("\n✅ Server stopped by user")
        sys.exit(0)
    except Exception as server_error:
        logger.error(f"Server error: {str(server_error)}", exc_info=True)
        sys.exit(1)


if __name__ == '__main__':
    main()
