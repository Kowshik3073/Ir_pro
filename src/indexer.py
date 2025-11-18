"""
Indexer Module: Creates and manages the inverted index for travel spots
"""
import json
import math
from collections import defaultdict
from typing import Dict, List, Set


class TravelSpotIndexer:
    """
    Builds and maintains an inverted index for travel spots.
    Uses TF-IDF for text-based similarity and metadata-based indexing.
    """
    
    def __init__(self):
        self.inverted_index = defaultdict(set)  # term -> set of spot ids
        self.spot_metadata = {}  # spot id -> metadata dict
        self.mood_index = defaultdict(set)  # mood -> set of spot ids
        self.spots_data = []
        self.doc_frequencies = defaultdict(int)  # term -> document frequency
        self.total_docs = 0
    
    def load_dataset(self, filepath: str) -> None:
        """Load travel spots dataset from JSON file"""
        with open(filepath, 'r') as f:
            data = json.load(f)
            self.spots_data = data['travel_spots']
            self.total_docs = len(self.spots_data)
    
    def build_index(self) -> None:
        """
        Build inverted index for all travel spots.
        Indexes: names, descriptions, and moods
        """
        for spot in self.spots_data:
            spot_id = spot['id']
            
            # Store metadata
            self.spot_metadata[spot_id] = {
                'name': spot['name'],
                'mood': spot['mood'],
                'budget_min': spot['budget_min'],
                'budget_max': spot['budget_max'],
                'duration_days': spot['duration_days'],
                'distance_km': spot['distance_km'],
                'rating': spot['rating'],
                'description': spot['description'],
                'best_months': spot.get('best_months', [])
            }
            
            # Index moods
            for mood in spot['mood']:
                self.mood_index[mood.lower()].add(spot_id)
            
            # Index text fields (name, description)
            text_to_index = (spot['name'] + ' ' + spot['description']).lower()
            terms = self._tokenize(text_to_index)
            
            for term in set(terms):  # Use set to count unique terms per doc
                self.inverted_index[term].add(spot_id)
                self.doc_frequencies[term] += 1
    
    def _tokenize(self, text: str) -> List[str]:
        """Simple tokenization: split by spaces and remove special chars"""
        import re
        # Remove special characters and split
        tokens = re.sub(r'[^a-zA-Z0-9\s]', '', text).split()
        return [t for t in tokens if len(t) > 2]  # Filter short tokens
    
    def get_spot_by_id(self, spot_id: int) -> Dict:
        """Retrieve spot metadata by ID"""
        return self.spot_metadata.get(spot_id)
    
    def get_spots_by_mood(self, mood: str) -> Set[int]:
        """Get all spot IDs matching a mood"""
        return self.mood_index.get(mood.lower(), set())
    
    def calculate_idf(self, term: str) -> float:
        """Calculate Inverse Document Frequency"""
        if term not in self.doc_frequencies:
            return 0.0
        return math.log(self.total_docs / self.doc_frequencies[term])
    
    def get_indexed_spots(self) -> Dict:
        """Return all indexed spots for debugging"""
        return self.spot_metadata
