"""
Core Recommendation Engine: Coordinates indexing, query interpretation, and scoring

Delivers a comprehensive Information Retrieval workflow:
1. Query Interpretation: Transform natural language to structured filters
2. Scoring: Compute and order destinations based on filters  
3. Presentation: Return results with explanations

Development Team: Destination Discovery Platform
Release: 2.0
"""
import logging
from typing import Dict, List

from src.indexer import TravelSpotIndexer
from src.query_processor import QueryProcessor
from src.ranker import TravelSpotRanker

logger = logging.getLogger(__name__)


class TravelSpotRecommendationSystem:
    """
    Comprehensive IR engine for destination recommendations.
    
    Workflow: Query -> Interpret -> Score -> Explain -> Return results
    
    Core Modules:
    - Indexer: Handles reverse index and metadata
    - QueryProcessor: Parses filters from natural language
    - Ranker: Computes and orders destinations based on filters
    """
    
    def __init__(self, dataset_path: str):
        """
        Set up the recommendation engine with dataset.
        
        Args:
            dataset_path: Location of travel_spots.json dataset file
            
        Raises:
            FileNotFoundError: If dataset file is missing
            json.JSONDecodeError: If dataset file has invalid JSON
        """
        try:
            self.data_indexer = TravelSpotIndexer()
            self.query_interpreter = QueryProcessor()
            
            # Import and index dataset
            self.data_indexer.load_dataset(dataset_path)
            self.data_indexer.build_index()
            
            self.scoring_engine = TravelSpotRanker(self.data_indexer)
            logger.info(f"Engine initialized with {len(self.data_indexer.destination_info)} destinations")
        except Exception as initialization_error:
            logger.error(f"Failed to initialize recommendation engine: {str(initialization_error)}")
            raise
    
    def recommend_with_explanation(self, user_query: str, top_k: int = 10) -> Dict:
        """
        Get destination recommendations with complete details and explanation.
        
        Args:
            user_query: Natural language query from user
            top_k: Number of recommendations to return (default: 5)
        
        Returns:
            Dictionary containing:
            - recommendations: List of recommended destinations
            - total_results: Total number of matching results
            - parsed_constraints: The filters extracted from query
        """
        try:
            # Phase 1: Interpret query to extract filters
            extracted_filters = self.query_interpreter.process_query(user_query)
            logger.debug(f"Query interpreted: {extracted_filters}")
            
            # Phase 2: Score destinations based on filters
            scored_destinations = self.scoring_engine.rank_spots(extracted_filters, top_k=top_k)
            
            # Phase 3: Format results for output
            formatted_recommendations = []
            for position, (destination_id, relevance_score, destination_data) in enumerate(scored_destinations, 1):
                recommendation_entry = {
                    'rank': position,
                    'spot_id': destination_id,
                    'name': destination_data['name'],
                    'relevance_score': round(relevance_score, 4),
                    'moods': destination_data['mood'],
                    'budget_range': f"₹{destination_data['budget_min']}-{destination_data['budget_max']}",
                    'budget_min': destination_data['budget_min'],
                    'budget_max': destination_data['budget_max'],
                    'duration_days': destination_data['duration_days'],
                    'distance_km': destination_data['distance_km'],
                    'rating': destination_data['rating'],
                    'best_months': destination_data.get('best_months', []),
                    'description': destination_data['description']
                }
                formatted_recommendations.append(recommendation_entry)
            
            logger.info(f"Generated {len(formatted_recommendations)} recommendations for query: '{user_query}'")
            
            return {
                'recommendations': formatted_recommendations,
                'total_results': len(formatted_recommendations),
                'parsed_constraints': extracted_filters
            }
            
        except Exception as processing_error:
            logger.error(f"Error generating recommendations: {str(processing_error)}")
            raise

    def recommend(self, user_query: str, top_k: int = 10) -> List[Dict]:
        """
        Compatibility wrapper.
        Returns just the list of recommendations.
        """
        output = self.recommend_with_explanation(user_query, top_k)
        return output['recommendations']
    
    def get_all_spots(self) -> List[Dict]:
        """
        Get all indexed destinations.
        
        Useful for displaying complete destination catalog.
        
        Returns:
            List of all destinations with basic metadata
        """
        try:
            all_destinations = [
                {
                    'id': destination_id,
                    'name': destination_data['name'],
                    'moods': destination_data['mood'],
                    'budget': f"₹{destination_data['budget_min']}-{destination_data['budget_max']}",
                    'budget_min': destination_data['budget_min'],
                    'budget_max': destination_data['budget_max'],
                    'duration': f"{destination_data['duration_days']} days",
                    'duration_days': destination_data['duration_days'],
                    'distance': f"{destination_data['distance_km']} km",
                    'distance_km': destination_data['distance_km'],
                    'rating': destination_data['rating'],
                    'best_months': destination_data.get('best_months', []),
                    'description': destination_data['description']
                }
                for destination_id, destination_data in self.data_indexer.destination_info.items()
            ]
            logger.info(f"Returned {len(all_destinations)} total destinations")
            return all_destinations
        except Exception as retrieval_error:
            logger.error(f"Error retrieving all destinations: {str(retrieval_error)}")
            raise
