"""
Indexer Module: Creates and manages the inverted index for travel spots

Provides fast lookups and text-based similarity search using:
- Inverted index for keyword search
- Mood-based indexing for mood queries  
- TF-IDF for relevance ranking
- Metadata caching for quick access

Author: Travel Recommendation Team
Version: 2.0
"""
import json
import math
import re
from collections import defaultdict
from typing import Dict, List, Set, Optional
from pathlib import Path


class TravelSpotIndexer:
    """
    Builds and maintains an inverted index for travel spots.
    
    Supports:
    - Keyword search via inverted index
    - Mood-based filtering
    - TF-IDF scoring
    - Metadata caching
    """
    
    # Minimum token length to index
    MIN_TOKEN_LENGTH = 2
    
    def __init__(self):
        """Initialize empty indexes"""
        self.inverted_index = defaultdict(set)  # term -> set of spot ids
        self.spot_metadata = {}  # spot id -> metadata dict
        self.mood_index = defaultdict(set)  # mood -> set of spot ids
        self.spots_data = []  # raw spot data
        self.doc_frequencies = defaultdict(int)  # term -> document frequency
        self.total_docs = 0
        self.dataset_path = None
    
    def load_dataset(self, filepath: str) -> None:
        """
        Load travel spots dataset from JSON file.
        
        Args:
            filepath: Path to JSON file containing travel spots
            
        Raises:
            FileNotFoundError: If file doesn't exist
            json.JSONDecodeError: If file is not valid JSON
        """
        self.dataset_path = filepath
        
        try:
            with open(filepath, 'r') as f:
                data = json.load(f)
                self.spots_data = data.get('travel_spots', [])
                self.total_docs = len(self.spots_data)
        except FileNotFoundError:
            raise FileNotFoundError(f"Dataset file not found: {filepath}")
        except json.JSONDecodeError as e:
            raise json.JSONDecodeError(f"Invalid JSON in dataset: {str(e)}", e.doc, e.pos)
    
    def build_index(self) -> None:
        """
        Build inverted index for all travel spots.
        
        Indexes:
        - Spot names (keywords)
        - Spot descriptions (tokenized)
        - Moods (for mood-based filtering)
        
        Must call load_dataset() before this method.
        """
        # Clear existing indexes
        self.inverted_index.clear()
        self.spot_metadata.clear()
        self.mood_index.clear()
        self.doc_frequencies.clear()
        
        for spot in self.spots_data:
            spot_id = spot['id']
            
            # Store metadata for quick retrieval
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
            
            # Index moods for mood-based queries
            for mood in spot['mood']:
                self.mood_index[mood.lower()].add(spot_id)
            
            # Index text fields (name, description)
            text_to_index = (spot['name'] + ' ' + spot['description']).lower()
            terms = self._tokenize(text_to_index)
            
            # Add to inverted index (use set to avoid duplicate counting)
            for term in set(terms):
                self.inverted_index[term].add(spot_id)
                self.doc_frequencies[term] += 1
    
    def _tokenize(self, text: str) -> List[str]:
        """
        Tokenize text into searchable terms.
        
        - Removes special characters
        - Converts to lowercase
        - Filters out short tokens
        
        Args:
            text: Text to tokenize
            
        Returns:
            List of tokens (words)
        """
        # Remove special characters and split by whitespace
        tokens = re.sub(r'[^a-zA-Z0-9\s]', '', text).split()
        # Filter short tokens for better search quality
        return [t for t in tokens if len(t) > self.MIN_TOKEN_LENGTH]
    
    def get_spot_by_id(self, spot_id: int) -> Optional[Dict]:
        """
        Retrieve spot metadata by ID.
        
        Args:
            spot_id: Numeric ID of the spot
            
        Returns:
            Metadata dictionary or None if not found
        """
        return self.spot_metadata.get(spot_id)
    
    def get_spots_by_mood(self, mood: str) -> Set[int]:
        """
        Get all spot IDs matching a mood.
        
        Args:
            mood: Mood string (e.g., 'relaxing', 'adventure')
            
        Returns:
            Set of matching spot IDs
        """
        return self.mood_index.get(mood.lower(), set())
    
    def calculate_idf(self, term: str) -> float:
        """
        Calculate Inverse Document Frequency (IDF) for a term.
        
        IDF = log(total_docs / docs_with_term)
        
        Higher IDF means the term is more unique/discriminative.
        
        Args:
            term: Search term
            
        Returns:
            IDF score (0.0 if term not found)
        """
        if term not in self.doc_frequencies or self.total_docs == 0:
            return 0.0
        return math.log(self.total_docs / self.doc_frequencies[term])
    
    def get_indexed_spots(self) -> Dict:
        """
        Return all indexed spots for debugging/inspection.
        
        Returns:
            Dictionary of all spot metadata indexed
        """
        return self.spot_metadata.copy()
