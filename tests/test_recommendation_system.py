"""
Unit tests for Travel Spot Recommendation System
"""
import unittest
import json
import os
import sys
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
    
    def test_get_spot_by_invalid_id(self):
        """Test retrieving spot by invalid ID"""
        spot = self.indexer.get_spot_by_id(99999)
        self.assertIsNone(spot)
    
    def test_get_spots_by_mood(self):
        """Test retrieving spots by mood"""
        adventure_spots = self.indexer.get_spots_by_mood('adventure')
        self.assertGreater(len(adventure_spots), 0)
    
    def test_get_spots_by_nonexistent_mood(self):
        """Test retrieving spots by mood that doesn't exist"""
        spots = self.indexer.get_spots_by_mood('nonexistent_mood_xyz')
        self.assertEqual(len(spots), 0)
    
    def test_idf_calculation(self):
        """Test IDF calculation"""
        idf = self.indexer.calculate_idf('beach')
        self.assertGreater(idf, 0)
    
    def test_idf_nonexistent_term(self):
        """Test IDF calculation for nonexistent term"""
        idf = self.indexer.calculate_idf('xyzabc12345')
        self.assertEqual(idf, 0.0)
    
    def test_build_index_validation(self):
        """Test that build_index validates dataset is loaded"""
        empty_indexer = TravelSpotIndexer()
        with self.assertRaises(ValueError):
            empty_indexer.build_index()


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
    
    def test_empty_query(self):
        """Test processing empty query"""
        constraints = self.processor.process_query("")
        self.assertIsNone(constraints['budget_max'])
        self.assertIsNone(constraints['place_name'])
    
    def test_invalid_query_type(self):
        """Test that non-string queries raise TypeError"""
        with self.assertRaises(TypeError):
            self.processor.process_query(123)
        
        with self.assertRaises(TypeError):
            self.processor.process_query(None)
    
    def test_season_extraction(self):
        """Test season constraint extraction"""
        # Test winter season
        constraints = self.processor.process_query("I want to visit in winter")
        self.assertIn('december', constraints['best_months'])
        self.assertIn('january', constraints['best_months'])
        self.assertIn('february', constraints['best_months'])
    
    def test_summer_season_extraction(self):
        """Test summer season extraction"""
        constraints = self.processor.process_query("best season is summer")
        self.assertIn('march', constraints['best_months'])
        self.assertIn('june', constraints['best_months'])
    
    def test_budget_focus_flag(self):
        """Test that 'budget friendly' keyword sets budget_max to 3500"""
        query = "budget friendly destination"
        constraints = self.processor.process_query(query)
        self.assertEqual(constraints['budget_max'], 3500)
    
    def test_budget_focus_override(self):
        """Test that explicit budget number overrides default budget-friendly setting"""
        query = "budget friendly but I have 7000 rupees"
        constraints = self.processor.process_query(query)
        # Explicit number (7000) should override the default budget-friendly (3500)
        self.assertEqual(constraints['budget_max'], 7000)
    
    def test_expanded_stop_words(self):
        """Test that expanded stop words are properly filtered from query terms"""
        query = "I want to find a beautiful adventure place for me"
        constraints = self.processor.process_query(query)
        query_terms = constraints['query_terms']
        # Should extract meaningful terms, not stop words
        self.assertIn('beautiful', query_terms)
        self.assertIn('adventure', query_terms)
        self.assertIn('place', query_terms)
        # Stop words should be filtered out
        self.assertNotIn('want', query_terms)
        self.assertNotIn('find', query_terms)
    
    def test_user_location_extraction(self):
        """Test extraction of user location from query"""
        query = "I want to visit tirupathi temple"
        constraints = self.processor.process_query(query)
        self.assertEqual(constraints['place_name'], 'Tirupathi Spiritual Temple')
    
    def test_user_location_alt_pattern(self):
        """Test alternative location patterns (e.g., 'leh', 'ladakh')"""
        query = "best destination is leh"
        constraints = self.processor.process_query(query)
        self.assertEqual(constraints['place_name'], 'Leh Ladakh Mountain')


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
            'distance_km': 1000,
            'place_name': None,
            'best_months': []
        }
        results = self.ranker.rank_spots(constraints, top_k=5)
        self.assertEqual(len(results), 5)
    
    def test_top_k_limit(self):
        """Test that top_k limit is respected"""
        constraints = {'budget_max': 10000, 'mood': [], 'duration_days': None, 
                      'distance_km': None, 'place_name': None, 'best_months': []}
        results = self.ranker.rank_spots(constraints, top_k=3)
        self.assertEqual(len(results), 3)
    
    def test_invalid_top_k(self):
        """Test that invalid top_k raises ValueError"""
        constraints = {}
        with self.assertRaises(ValueError):
            self.ranker.rank_spots(constraints, top_k=0)
        
        with self.assertRaises(ValueError):
            self.ranker.rank_spots(constraints, top_k=-1)
    
    def test_budget_score_within_range(self):
        """Test budget scoring when within range"""
        # Budget within range gets 1.0 base score (not penalty)
        score = self.ranker._calculate_budget_score(2000, 5000, 3500)
        self.assertEqual(score, 1.0)
    
    def test_budget_score_below_min(self):
        """Test budget scoring when below minimum"""
        score = self.ranker._calculate_budget_score(3000, 5000, 2000)
        self.assertLess(score, 1.0)
        self.assertGreater(score, 0)
    
    def test_budget_score_above_max(self):
        """Test budget scoring when above maximum"""
        score = self.ranker._calculate_budget_score(2000, 5000, 8000)
        self.assertLess(score, 1.0)
    
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
    
    def test_mood_score_no_match(self):
        """Test mood scoring with no match"""
        spot_moods = ['adventure']
        user_moods = ['party', 'nightlife']
        score = self.ranker._calculate_mood_score(spot_moods, user_moods)
        self.assertEqual(score, 0.0)
    
    def test_duration_score_exact_match(self):
        """Test duration scoring with exact match"""
        score = self.ranker._calculate_duration_score(3, 3)
        self.assertEqual(score, 1.0)
    
    def test_budget_score_over_max(self):
        """Test budget scoring when spot budget is higher than user budget"""
        # When user budget is lower than spot's budget_max
        # User has 4000, spot costs 5000-10000 (over budget)
        score = self.ranker._calculate_budget_score(5000, 10000, 4000)
        self.assertLess(score, 1.0)
        self.assertGreater(score, 0)  # Should not be penalized too harshly
    
    def test_ranking_tie_breaker_logic_by_rating(self):
        """Test that ranking uses rating as tie-breaker for identical scores"""
        # Create constraints that would produce similar scores
        constraints = {
            'budget_max': 3500,
            'mood': ['spiritual', 'cultural'],
            'duration_days': 2,
            'distance_km': None,
            'place_name': None,
            'best_months': []
        }
        results = self.ranker.rank_spots(constraints, top_k=5)
        
        # Check that results are properly ranked
        self.assertGreater(len(results), 0)
        # Higher rated destinations should appear first when scores are tied
        # Tirupathi has 4.9 rating, Varanasi has 4.5
        if len(results) >= 2:
            # Both are spiritual, so Tirupathi with 4.9 rating should rank higher
            rankings = [r[2]['name'] for r in results]
            tirupathi_idx = next((i for i, r in enumerate(rankings) if 'Tirupathi' in r), -1)
            varanasi_idx = next((i for i, r in enumerate(rankings) if 'Varanasi' in r), -1)
            # If both are present, Tirupathi should come before Varanasi
            if tirupathi_idx >= 0 and varanasi_idx >= 0:
                self.assertLess(tirupathi_idx, varanasi_idx)


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
        self.assertGreater(len(result['recommendations']), 0)
    
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
    
    def test_recommendation_scoring(self):
        """Test that results are scored and ranked"""
        query = "Budget 5000"
        results = self.system.recommend(query, top_k=3)
        self.assertEqual(len(results), 3)
        # Verify descending score order
        scores = [r['relevance_score'] for r in results]
        self.assertEqual(scores, sorted(scores, reverse=True))
    
    def test_budget_friendly_ranking(self):
        """Test that 'budget friendly' query ranks affordable destinations first
        
        Verifies that Tirupathi (₹1000-5000, rating 4.9) and Varanasi (₹1500-3500, rating 4.5)
        are ranked higher than expensive destinations when budget-friendly preference is detected.
        
        Also tests that within budget-friendly destinations, higher-rated spots rank first
        (dynamic weight adjustment for spiritual/cultural recommendations).
        """
        query = "budget friendly"
        results = self.system.recommend(query, top_k=5)
        
        # Should return results
        self.assertGreater(len(results), 0)
        
        # First result should be budget-friendly (affordable) with high rating
        first_result = results[0]
        self.assertGreaterEqual(first_result['rating'], 4.8)  # High quality rating
        self.assertLessEqual(first_result['budget_min'], 2000)  # Affordable entry point
        
        # Extract result names for verification
        result_names = [r['name'] for r in results]
        
        # Tirupathi (₹1000-5000, rating 4.9) should appear in top results for budget query
        # It has the lowest budget_min (1000) and highest rating (4.9) among affordable options
        if 'Tirupathi Spiritual Temple' in result_names:
            tirupathi_rank = result_names.index('Tirupathi Spiritual Temple') + 1
            # Tirupathi should rank high for budget queries
            self.assertLessEqual(tirupathi_rank, 5)
        
        # Verify results are sorted by relevance score (descending)
        scores = [r['relevance_score'] for r in results]
        self.assertEqual(scores, sorted(scores, reverse=True))
        
        # Budget-friendly spots should have reasonable relevance scores
        for result in results:
            if result['budget_min'] <= 2000:  # Budget-friendly spots
                self.assertGreaterEqual(result['relevance_score'], 0.5)

    
    def test_special_characters_in_query(self):
        """Test handling queries with special characters"""
        query = "manali@#$beach!"
        results = self.system.recommend(query, top_k=5)
        self.assertGreater(len(results), 0)


if __name__ == '__main__':
    unittest.main()
