"""
DataIndexBuilder: Constructs and maintains reverse lookup structures for destinations

Delivers rapid retrieval and text similarity analysis through:
- Reverse keyword mapping for term-based search
- Atmosphere-based categorization for vibe filtering  
- TF-IDF weighting for relevance computation
- Quick-access metadata storage

Development Team: Destination Discovery Platform
Release: 2.0
"""
import json
import logging
import math
import re
from collections import defaultdict
from typing import Dict, List, Set, Optional

logger = logging.getLogger(__name__)


class TravelSpotIndexer:
    """
    Constructs and manages reverse lookup structures for destination data.
    
    Features:
    - Term-based retrieval via reverse index
    - Atmosphere-based categorization
    - TF-IDF relevance weighting
    - Fast metadata access
    """
    
    # Shortest acceptable word length for indexing
    SHORTEST_WORD_LEN = 2
    
    def __init__(self):
        """Set up empty data structures"""
        self.reverse_term_map = defaultdict(set)  # word -> destination ID collection
        self.destination_info = {}  # destination ID -> info dictionary
        self.vibe_catalog = defaultdict(set)  # atmosphere -> destination ID collection
        self.raw_destination_list = []  # unprocessed destination records
        self.term_occurrence_counts = defaultdict(int)  # word -> occurrence count
        self.total_destination_count = 0
        self.source_file_path = None
        self._idf_lookup_cache = {}  # Cached IDF computations
    
    def load_dataset(self, filepath: str) -> None:
        """
        Import destination records from JSON data file.
        
        Args:
            filepath: Location of JSON file with destination data
            
        Raises:
            FileNotFoundError: If specified file is missing
            json.JSONDecodeError: If file contains malformed JSON
            ValueError: If data structure doesn't match expected format
        """
        self.source_file_path = filepath
        
        try:
            if not filepath or not filepath.strip():
                raise ValueError("File path must not be blank")
                
            with open(filepath, 'r', encoding='utf-8') as file_handle:
                json_content = json.load(file_handle)
                
            if not isinstance(json_content, dict) or 'travel_spots' not in json_content:
                raise ValueError("Data must be dictionary containing 'travel_spots' field")
                
            if not isinstance(json_content['travel_spots'], list):
                raise ValueError("'travel_spots' field must contain a list")
                
            self.raw_destination_list = json_content['travel_spots']
            self.total_destination_count = len(self.raw_destination_list)
            logger.debug(f"Imported {self.total_destination_count} destinations from {filepath}")
            
        except FileNotFoundError:
            logger.error(f"Cannot locate data file: {filepath}")
            raise FileNotFoundError(f"Cannot locate data file: {filepath}")
        except json.JSONDecodeError as parse_error:
            logger.error(f"Malformed JSON detected: {str(parse_error)}")
            raise json.JSONDecodeError(f"Malformed JSON detected: {str(parse_error)}", parse_error.doc, parse_error.pos)
        except ValueError as validation_error:
            logger.error(f"Data structure validation failed: {str(validation_error)}")
            raise
    
    def build_index(self) -> None:
        """
        Construct reverse lookup structures for all destinations.
        
        Processes:
        - Destination titles (keyword extraction)
        - Destination details (word tokenization)
        - Atmosphere tags (for vibe-based filtering)
        
        Raises:
            ValueError: If data hasn't been imported yet
            
        Must invoke load_dataset() prior to calling this.
        """
        if not self.raw_destination_list:
            raise ValueError("Data must be imported first. Invoke load_dataset() before indexing.")
            
        # Reset all lookup structures
        self.reverse_term_map.clear()
        self.destination_info.clear()
        self.vibe_catalog.clear()
        self.term_occurrence_counts.clear()
        self._idf_lookup_cache.clear()  # Flush cache on rebuild
        logger.debug("Constructing reverse index for all destinations")
        
        for destination_record in self.raw_destination_list:
            destination_identifier = destination_record['id']
            
            # Cache metadata for rapid access
            self.destination_info[destination_identifier] = {
                'name': destination_record['name'],
                'mood': destination_record['mood'],
                'budget_min': destination_record['budget_min'],
                'budget_max': destination_record['budget_max'],
                'duration_days': destination_record['duration_days'],
                'distance_km': destination_record['distance_km'],
                'rating': destination_record['rating'],
                'description': destination_record['description'],
                'best_months': destination_record.get('best_months', [])
            }
            
            # Build atmosphere-based lookup
            for atmosphere_tag in destination_record['mood']:
                self.vibe_catalog[atmosphere_tag.lower()].add(destination_identifier)
            
            # Process text content (title + details)
            combined_text = (destination_record['name'] + ' ' + destination_record['description']).lower()
            word_tokens = self._break_into_words(combined_text)
            
            # Populate reverse index (deduplicate with set)
            for unique_word in set(word_tokens):
                self.reverse_term_map[unique_word].add(destination_identifier)
                self.term_occurrence_counts[unique_word] += 1
    
    def _break_into_words(self, text_input: str) -> List[str]:
        """
        Convert text into individual searchable words.
        
        - Strips punctuation and special symbols
        - Normalizes to lowercase
        - Removes very short words
        
        Args:
            text_input: Text to process
            
        Returns:
            List of word tokens
        """
        # Strip non-alphanumeric characters and split on whitespace
        word_tokens = re.sub(r'[^a-zA-Z0-9\s]', '', text_input).split()
        # Keep only words meeting minimum length
        return [word for word in word_tokens if len(word) > self.SHORTEST_WORD_LEN]
    
    def get_spot_by_id(self, spot_id: int) -> Optional[Dict]:
        """
        Fetch destination information using its identifier.
        
        Args:
            spot_id: Unique destination identifier
            
        Returns:
            Information dictionary or None if not indexed
        """
        return self.destination_info.get(spot_id)
    
    def get_spots_by_mood(self, mood: str) -> Set[int]:
        """
        Retrieve all destination IDs with a specific atmosphere.
        
        Args:
            mood: Atmosphere descriptor (e.g., 'relaxing', 'adventure')
            
        Returns:
            Collection of matching destination IDs
        """
        return self.vibe_catalog.get(mood.lower(), set())
    
    def calculate_idf(self, term: str) -> float:
        """
        Compute Inverse Document Frequency (IDF) for a search term.
        
        Formula: IDF = log(total_destinations / destinations_containing_term)
        
        Higher values indicate more distinctive/rare terms.
        Computations are cached to improve performance.
        
        Args:
            term: Word to analyze
            
        Returns:
            IDF weight (0.0 if term not indexed)
        """
        # Use cached value if available
        if term in self._idf_lookup_cache:
            return self._idf_lookup_cache[term]
            
        if term not in self.term_occurrence_counts or self.total_destination_count == 0:
            computed_value = 0.0
        else:
            computed_value = math.log(self.total_destination_count / self.term_occurrence_counts[term])
        
        # Store for future lookups
        self._idf_lookup_cache[term] = computed_value
        return computed_value
    
    def get_indexed_spots(self) -> Dict:
        """
        Export all indexed destination data for inspection.
        
        Returns:
            Copy of complete destination metadata dictionary
        """
        return self.destination_info.copy()
