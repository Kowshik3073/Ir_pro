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
from typing import Dict, Any, Optional

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
        elif self.path == '/api/add-place':
            self.handle_add_place()
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
        if self.path.startswith('/api/remove-place/'):
            self.handle_remove_place()
        else:
            self.send_error(404)
    
    def handle_recommend(self):
        """
        Handle recommendation request.
        
        Expected JSON:
        {
            "query": "string",
            "top_k": int (optional, default 5)
        }
        """
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length).decode('utf-8')
            data = json.loads(body)
            
            query = data.get('query', '').strip()
            top_k = data.get('top_k', 5)
            
            if not query:
                return self.send_error_response(400, "Query is required")
            
            if not isinstance(top_k, int) or top_k < 1:
                return self.send_error_response(400, "top_k must be a positive integer")
            
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
            logger.info(f"Recommendation request: query='{query}', top_k={top_k}")
            
        except json.JSONDecodeError:
            self.send_error_response(400, "Invalid JSON in request body")
        except Exception as e:
            logger.error(f"Error in recommendation: {str(e)}")
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
    
    def handle_add_place(self):
        """
        Handle adding a new place.
        
        Expected JSON:
        {
            "name": "string",
            "mood": ["string"],
            "budget_min": int,
            "budget_max": int,
            "duration_days": int,
            "distance_km": int,
            "rating": float,
            "best_months": ["string"],
            "description": "string"
        }
        """
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length).decode('utf-8')
            data = json.loads(body)
            
            # Validate required fields
            required_fields = ['name', 'mood', 'budget_min', 'budget_max', 
                             'duration_days', 'distance_km', 'rating', 'description']
            missing_fields = [f for f in required_fields if f not in data or data[f] == '']
            
            if missing_fields:
                return self.send_error_response(400, f"Missing required fields: {', '.join(missing_fields)}")
            
            # Load current data
            dataset_path = self._get_dataset_path()
            with open(dataset_path, 'r') as f:
                travel_data = json.load(f)
            
            # Find next ID
            max_id = max([spot['id'] for spot in travel_data['travel_spots']], default=0)
            new_id = max_id + 1
            
            # Create new spot with validation
            new_spot = {
                'id': new_id,
                'name': str(data.get('name', '')).strip(),
                'mood': data.get('mood', []),
                'budget_min': int(data.get('budget_min', 0)),
                'budget_max': int(data.get('budget_max', 0)),
                'duration_days': int(data.get('duration_days', 0)),
                'distance_km': int(data.get('distance_km', 0)),
                'rating': float(data.get('rating', 0)),
                'best_months': data.get('best_months', []),
                'description': str(data.get('description', '')).strip()
            }
            
            # Validate budget range
            if new_spot['budget_min'] > new_spot['budget_max']:
                return self.send_error_response(400, "budget_min cannot be greater than budget_max")
            
            # Validate rating
            if not 0 <= new_spot['rating'] <= 5:
                return self.send_error_response(400, "rating must be between 0 and 5")
            
            # Add to data
            travel_data['travel_spots'].append(new_spot)
            
            # Save updated data
            with open(dataset_path, 'w') as f:
                json.dump(travel_data, f, indent=2)
            
            # Reload recommendation system
            recommendation_system.indexer.load_dataset(dataset_path)
            recommendation_system.indexer.build_index()
            
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            
            response = {
                'success': True,
                'message': f'Place "{new_spot["name"]}" added successfully',
                'place': new_spot
            }
            
            self.wfile.write(json.dumps(response).encode('utf-8'))
            logger.info(f"Added new place: {new_spot['name']} (ID: {new_id})")
            
        except json.JSONDecodeError:
            self.send_error_response(400, "Invalid JSON in request body")
        except ValueError as e:
            self.send_error_response(400, f"Invalid data type: {str(e)}")
        except Exception as e:
            logger.error(f"Error adding place: {str(e)}")
            self.send_error_response(500, f"Error adding place: {str(e)}")
    
    def handle_remove_place(self):
        """
        Handle removing a place by ID.
        
        Path: /api/remove-place/<id>
        """
        try:
            # Extract place ID from path
            try:
                place_id = int(self.path.split('/')[-1])
            except (ValueError, IndexError):
                return self.send_error_response(400, "Invalid place ID format")
            
            # Load current data
            dataset_path = self._get_dataset_path()
            with open(dataset_path, 'r') as f:
                travel_data = json.load(f)
            
            # Find and remove spot
            original_count = len(travel_data['travel_spots'])
            travel_data['travel_spots'] = [
                spot for spot in travel_data['travel_spots'] 
                if spot['id'] != place_id
            ]
            
            if len(travel_data['travel_spots']) == original_count:
                return self.send_error_response(404, f'Place with ID {place_id} not found')
            
            # Save updated data
            with open(dataset_path, 'w') as f:
                json.dump(travel_data, f, indent=2)
            
            # Reload recommendation system
            recommendation_system.indexer.load_dataset(dataset_path)
            recommendation_system.indexer.build_index()
            
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            
            response = {
                'success': True,
                'message': f'Place with ID {place_id} removed successfully'
            }
            
            self.wfile.write(json.dumps(response).encode('utf-8'))
            logger.info(f"Removed place with ID: {place_id}")
            
        except Exception as e:
            logger.error(f"Error removing place: {str(e)}")
            self.send_error_response(500, f"Error removing place: {str(e)}")
    
    def send_error_response(self, code: int, message: str) -> None:
        """
        Send a JSON error response.
        
        Args:
            code: HTTP status code
            message: Error message
        """
        self.send_response(code)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        
        response = {
            'success': False,
            'error': message,
            'code': code
        }
        
        self.wfile.write(json.dumps(response).encode('utf-8'))
    
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
        logger.info("  POST   /api/add-place        - Add new place")
        logger.info("  DELETE /api/remove-place/<id> - Remove place")
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
