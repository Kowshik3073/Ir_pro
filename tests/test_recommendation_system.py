"""
Unit tests for Travel Spot Recommendation System
"""
import unittest
import json
import os
from src.indexer import TravelSpotIndexer
from src.query_processor import QueryProcessor
from src.ranker import TravelSpotRanker
from src.recommendation_system import TravelSpotRecommendationSystem


class TestIndexer(unittest.TestCase):
    """Test indexing functionality"""
    
    def setUp(self):
        self.indexer = TravelSpotIndexer()
        dataset_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'travel_spots.json')
        self.indexer.load_dataset(dataset_path)
        self.indexer.build_index()
    
    def test_dataset_loaded(self):
        """Test that dataset is loaded correctly"""
        self.assertGreater(len(self.indexer.spots_data), 0)
    
    def test_index_built(self):
        """Test that index is built"""
        self.assertGreater(len(self.indexer.spot_metadata), 0)
        self.assertGreater(len(self.indexer.inverted_index), 0)
    
    def test_get_spot_by_id(self):
        """Test retrieving spot by ID"""
        spot = self.indexer.get_spot_by_id(1)
        self.assertIsNotNone(spot)
        self.assertEqual(spot['name'], 'Goa Beach')
    
    def test_get_spots_by_mood(self):
        """Test retrieving spots by mood"""
        adventure_spots = self.indexer.get_spots_by_mood('adventure')
        self.assertGreater(len(adventure_spots), 0)
    
    def test_idf_calculation(self):
        """Test IDF calculation"""
        idf = self.indexer.calculate_idf('beach')
        self.assertGreater(idf, 0)


class TestQueryProcessor(unittest.TestCase):
    """Test query processing"""
    
    def setUp(self):
        self.processor = QueryProcessor()
    
    def test_budget_extraction(self):
        """Test budget constraint extraction"""
        query = "I have 5000 rupees"
        constraints = self.processor.process_query(query)
        self.assertEqual(constraints['budget_max'], 5000)
    
    def test_mood_extraction(self):
        """Test mood constraint extraction"""
        query = "I want adventure and nature"
        constraints = self.processor.process_query(query)
        self.assertIn('adventure', constraints['mood'])
        self.assertIn('nature', constraints['mood'])
    
    def test_duration_extraction(self):
        """Test duration constraint extraction"""
        query = "I have 4 days"
        constraints = self.processor.process_query(query)
        self.assertEqual(constraints['duration_days'], 4)
    
    def test_distance_extraction(self):
        """Test distance constraint extraction"""
        query = "within 1000 km"
        constraints = self.processor.process_query(query)
        self.assertEqual(constraints['distance_km'], 1000)
    
    def test_complex_query(self):
        """Test parsing complex query"""
        query = "Budget 5000, want adventure for 4 days within 1000km"
        constraints = self.processor.process_query(query)
        self.assertEqual(constraints['budget_max'], 5000)
        self.assertIn('adventure', constraints['mood'])
        self.assertEqual(constraints['duration_days'], 4)
        self.assertEqual(constraints['distance_km'], 1000)


class TestRanker(unittest.TestCase):
    """Test ranking functionality"""
    
    def setUp(self):
        self.indexer = TravelSpotIndexer()
        dataset_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'travel_spots.json')
        self.indexer.load_dataset(dataset_path)
        self.indexer.build_index()
        self.ranker = TravelSpotRanker(self.indexer)
    
    def test_ranking_returns_results(self):
        """Test that ranking returns results"""
        constraints = {
            'budget_max': 5000,
            'mood': ['adventure'],
            'duration_days': 3,
            'distance_km': 1000
        }
        results = self.ranker.rank_spots(constraints, top_k=5)
        self.assertEqual(len(results), 5)
    
    def test_top_k_limit(self):
        """Test that top_k limit is respected"""
        constraints = {'budget_max': 10000}
        results = self.ranker.rank_spots(constraints, top_k=3)
        self.assertEqual(len(results), 3)
    
    def test_budget_score_within_range(self):
        """Test budget scoring when within range"""
        score = self.ranker._calculate_budget_score(2000, 5000, 3500)
        self.assertEqual(score, 1.0)
    
    def test_mood_score_full_match(self):
        """Test mood scoring with full match"""
        spot_moods = ['adventure', 'nature']
        user_moods = ['adventure', 'nature']
        score = self.ranker._calculate_mood_score(spot_moods, user_moods)
        self.assertEqual(score, 1.0)
    
    def test_mood_score_partial_match(self):
        """Test mood scoring with partial match"""
        spot_moods = ['adventure', 'nature']
        user_moods = ['adventure', 'party']
        score = self.ranker._calculate_mood_score(spot_moods, user_moods)
        self.assertEqual(score, 0.5)


class TestRecommendationSystem(unittest.TestCase):
    """Test complete recommendation system"""
    
    def setUp(self):
        dataset_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'travel_spots.json')
        self.system = TravelSpotRecommendationSystem(dataset_path)
    
    def test_recommend_returns_results(self):
        """Test that recommend returns results"""
        query = "I have 5000 rupees, want adventure for 4 days"
        results = self.system.recommend(query, top_k=5)
        self.assertGreater(len(results), 0)
    
    def test_recommend_with_explanation(self):
        """Test recommend with explanation"""
        query = "Budget 5000, adventure mood"
        result = self.system.recommend_with_explanation(query)
        self.assertIn('recommendations', result)
        self.assertIn('parsed_constraints', result)
    
    def test_get_all_spots(self):
        """Test getting all spots"""
        spots = self.system.get_all_spots()
        self.assertGreater(len(spots), 0)
    
    def test_result_format(self):
        """Test result format"""
        query = "Budget 3000"
        results = self.system.recommend(query, top_k=1)
        if results:
            result = results[0]
            self.assertIn('rank', result)
            self.assertIn('spot_id', result)
            self.assertIn('name', result)
            self.assertIn('relevance_score', result)
            self.assertIn('moods', result)
            self.assertIn('budget_range', result)


if __name__ == '__main__':
    unittest.main()
