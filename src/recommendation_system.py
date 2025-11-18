"""
Main Recommendation System: Orchestrates indexing, query processing, and ranking
"""
from src.indexer import TravelSpotIndexer
from src.query_processor import QueryProcessor
from src.ranker import TravelSpotRanker
from typing import Dict, List, Tuple


class TravelSpotRecommendationSystem:
    """
    Complete IR system for travel spot recommendations.
    Pipeline: Query -> Process -> Rank -> Return results
    """
    
    def __init__(self, dataset_path: str):
        """Initialize the recommendation system with dataset"""
        self.indexer = TravelSpotIndexer()
        self.query_processor = QueryProcessor()
        
        # Load and index dataset
        self.indexer.load_dataset(dataset_path)
        self.indexer.build_index()
        
        self.ranker = TravelSpotRanker(self.indexer)
    
    def recommend(self, user_query: str, top_k: int = 5) -> List[Dict]:
        """
        Get travel spot recommendations for a user query.
        
        Args:
            user_query: Natural language query from user
            top_k: Number of recommendations to return
        
        Returns:
            List of recommended spots with scores and metadata
        """
        # Step 1: Process query
        constraints = self.query_processor.process_query(user_query)
        
        # Step 2: Rank spots
        ranked_results = self.ranker.rank_spots(constraints, top_k=top_k)
        
        # Step 3: Format results
        recommendations = []
        for rank, (spot_id, score, metadata) in enumerate(ranked_results, 1):
            rec = {
                'rank': rank,
                'spot_id': spot_id,
                'name': metadata['name'],
                'relevance_score': round(score, 4),
                'moods': metadata['mood'],
                'budget_range': f"₹{metadata['budget_min']}-{metadata['budget_max']}",
                'duration_days': metadata['duration_days'],
                'distance_km': metadata['distance_km'],
                'rating': metadata['rating'],
                'description': metadata['description']
            }
            recommendations.append(rec)
        
        return recommendations
    
    def recommend_with_explanation(self, user_query: str, top_k: int = 5) -> Dict:
        """
        Get recommendations with detailed explanations of why spots were ranked.
        
        Returns:
            Dictionary with recommendations, constraints, and explanations
        """
        # Process query
        constraints = self.query_processor.process_query(user_query)
        
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
                'duration_days': metadata['duration_days'],
                'distance_km': metadata['distance_km'],
                'rating': metadata['rating'],
                'best_months': metadata.get('best_months', []),
                'description': metadata['description'],
                'score_breakdown': explanation['components']
            }
            recommendations.append(rec)
        
        return {
            'user_query': user_query,
            'parsed_constraints': constraints,
            'recommendations': recommendations,
            'total_results': len(recommendations)
        }
    
    def get_all_spots(self) -> List[Dict]:
        """Get all indexed travel spots"""
        return [
            {
                'id': spot_id,
                'name': metadata['name'],
                'moods': metadata['mood'],
                'budget': f"₹{metadata['budget_min']}-{metadata['budget_max']}",
                'duration': f"{metadata['duration_days']} days",
                'distance': f"{metadata['distance_km']} km",
                'rating': metadata['rating'],
                'best_months': metadata.get('best_months', [])
            }
            for spot_id, metadata in self.indexer.spot_metadata.items()
        ]
