"""
Main Recommendation System: Orchestrates indexing, query processing, and ranking

Implements a complete Information Retrieval pipeline:
1. Query Processing: Convert natural language to structured constraints
2. Ranking: Score and rank travel spots based on constraints  
3. Formatting: Return results with explanations

Author: Travel Recommendation Team
Version: 2.0
"""
import logging
from typing import Dict, List

from src.indexer import TravelSpotIndexer
from src.query_processor import QueryProcessor
from src.ranker import TravelSpotRanker

logger = logging.getLogger(__name__)


class TravelSpotRecommendationSystem:
    """
    Complete IR system for travel spot recommendations.
    
    Pipeline: Query -> Process -> Rank -> Explain -> Return results
    
    Components:
    - Indexer: Manages inverted index and metadata
    - QueryProcessor: Extracts constraints from natural language
    - Ranker: Scores and ranks spots based on constraints
    """
    
    def __init__(self, dataset_path: str):
        """
        Initialize the recommendation system with dataset.
        
        Args:
            dataset_path: Path to travel_spots.json dataset file
            
        Raises:
            FileNotFoundError: If dataset file doesn't exist
            json.JSONDecodeError: If dataset file is invalid JSON
        """
        try:
            self.indexer = TravelSpotIndexer()
            self.query_processor = QueryProcessor()
            
            # Load and index dataset
            self.indexer.load_dataset(dataset_path)
            self.indexer.build_index()
            
            self.ranker = TravelSpotRanker(self.indexer)
            logger.info(f"System initialized with {len(self.indexer.spot_metadata)} travel spots")
        except Exception as e:
            logger.error(f"Failed to initialize recommendation system: {str(e)}")
            raise
    
    def recommend(self, user_query: str, top_k: int = 5) -> List[Dict]:
        """
        Get travel spot recommendations for a user query.
        
        Args:
            user_query: Natural language query from user
            top_k: Number of recommendations to return (default: 5)
        
        Returns:
            List of recommended spots with scores and metadata
            
        Example:
            >>> system.recommend("budget 5000, adventure", top_k=3)
            [
                {
                    'rank': 1,
                    'name': 'Manali Hill Station',
                    'relevance_score': 0.8234,
                    'moods': ['adventure', 'nature'],
                    ...
                }
            ]
        """
        try:
            # Step 1: Process query to extract constraints
            constraints = self.query_processor.process_query(user_query)
            logger.debug(f"Query processed: {constraints}")
            
            # Step 2: Rank spots based on constraints
            ranked_results = self.ranker.rank_spots(constraints, top_k=top_k)
            
            # Step 3: Format results for return
            recommendations = []
            for rank, (spot_id, score, metadata) in enumerate(ranked_results, 1):
                rec = {
                    'rank': rank,
                    'spot_id': spot_id,
                    'name': metadata['name'],
                    'relevance_score': round(score, 4),
                    'moods': metadata['mood'],
                    'budget_range': f"₹{metadata['budget_min']}-{metadata['budget_max']}",
                    'budget_min': metadata['budget_min'],
                    'budget_max': metadata['budget_max'],
                    'duration_days': metadata['duration_days'],
                    'distance_km': metadata['distance_km'],
                    'rating': metadata['rating'],
                    'description': metadata['description']
                }
                recommendations.append(rec)
            
            logger.info(f"Generated {len(recommendations)} recommendations for query: '{user_query}'")
            return recommendations
            
        except Exception as e:
            logger.error(f"Error generating recommendations: {str(e)}")
            raise
    
    def recommend_with_explanation(self, user_query: str, top_k: int = 5) -> Dict:
        """
        Get recommendations with detailed explanations of ranking.
        
        Provides a complete breakdown of:
        - How the query was interpreted
        - Why each spot was ranked (score breakdown)
        - All metadata for informed decision-making
        
        Args:
            user_query: Natural language query from user
            top_k: Number of recommendations to return (default: 5)
        
        Returns:
            Dictionary with:
            - user_query: Original query
            - parsed_constraints: Extracted structured constraints
            - recommendations: List of spots with score breakdown
            - total_results: Number of results returned
        """
        try:
            # Process query
            constraints = self.query_processor.process_query(user_query)
            logger.debug(f"Query explained: {constraints}")
            
            # Rank spots
            ranked_results = self.ranker.rank_spots(constraints, top_k=top_k)
            
            # Build response with explanations
            recommendations = []
            for rank, (spot_id, score, metadata) in enumerate(ranked_results, 1):
                explanation = self.ranker.explain_score(spot_id, metadata, constraints)
                
                rec = {
                    'rank': rank,
                    'spot_id': spot_id,
                    'name': metadata['name'],
                    'relevance_score': round(score, 4),
                    'moods': metadata['mood'],
                    'budget_range': f"₹{metadata['budget_min']}-{metadata['budget_max']}",
                    'budget_min': metadata['budget_min'],
                    'budget_max': metadata['budget_max'],
                    'duration_days': metadata['duration_days'],
                    'distance_km': metadata['distance_km'],
                    'rating': metadata['rating'],
                    'best_months': metadata.get('best_months', []),
                    'description': metadata['description'],
                    'score_breakdown': explanation['components']
                }
                recommendations.append(rec)
            
            logger.info(f"Generated {len(recommendations)} explained recommendations")
            return {
                'user_query': user_query,
                'parsed_constraints': constraints,
                'recommendations': recommendations,
                'total_results': len(recommendations)
            }
            
        except Exception as e:
            logger.error(f"Error generating explained recommendations: {str(e)}")
            raise
    
    def get_all_spots(self) -> List[Dict]:
        """
        Get all indexed travel spots.
        
        Useful for displaying complete destination catalog.
        
        Returns:
            List of all spots with basic metadata
        """
        try:
            spots = [
                {
                    'id': spot_id,
                    'name': metadata['name'],
                    'moods': metadata['mood'],
                    'budget': f"₹{metadata['budget_min']}-{metadata['budget_max']}",
                    'budget_min': metadata['budget_min'],
                    'budget_max': metadata['budget_max'],
                    'duration': f"{metadata['duration_days']} days",
                    'duration_days': metadata['duration_days'],
                    'distance': f"{metadata['distance_km']} km",
                    'distance_km': metadata['distance_km'],
                    'rating': metadata['rating'],
                    'best_months': metadata.get('best_months', []),
                    'description': metadata['description']
                }
                for spot_id, metadata in self.indexer.spot_metadata.items()
            ]
            logger.info(f"Returned {len(spots)} total spots")
            return spots
        except Exception as e:
            logger.error(f"Error retrieving all spots: {str(e)}")
            raise
