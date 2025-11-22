"""
UserQueryParser: Transforms user input into structured search parameters

This module handles the conversion of free-form text queries into
organized search criteria for the travel destination retrieval system.

Core Capabilities:
- Destination identification
- Financial limit parsing
- Vibe/atmosphere detection
- Trip length extraction
- Travel range parsing
- Optimal timing identification
"""
from typing import Dict, List
import re


class QueryProcessor:
    """
    Interprets user search requests and builds structured filter criteria.
    Parses financial limits, atmosphere preferences, trip length, travel range, and locations.
    """
    
    # Atmosphere/vibe keyword catalog - grouped by experience type
    VIBE_LEXICON = {
        'adventure': ['adventure', 'trekking', 'hiking', 'extreme', 'thrill', 'trek', 'climb'],
        'nature': ['nature', 'wildlife', 'forest', 'scenic', 'landscape', 'hill', 'mountain', 'snow'],
        'relaxing': ['relax', 'chill', 'peaceful', 'calm', 'quiet', 'rest'],
        'party': ['party', 'nightlife', 'disco', 'club', 'fun', 'dance', 'night'],
        'cultural': ['culture', 'cultural', 'heritage', 'art', 'museum', 'city', 'tour'],
        'history': ['history', 'historical', 'ancient', 'monument', 'temple'],
        'spiritual': ['spiritual', 'meditation', 'yoga', 'zen', 'peace'],
        'romantic': ['romantic', 'couple', 'honeymoon', 'love']
    }
    
    # Location aliases for popular destinations
    DESTINATION_ALIASES = {
        'manali': 'Manali Hill Station',
        'goa': 'Goa Beach',
        'kerala': 'Kerala Backwaters',
        'kochi': 'Kerala Backwaters',
        'backwaters': 'Kerala Backwaters',
        'leh': 'Leh Ladakh Mountain',
        'ladakh': 'Leh Ladakh Mountain',
        'ooty': 'Ooty Hill Station',
        'shimla': 'Shimla Snow Mountain',
        'jaipur': 'Jaipur City Tour',
        'varanasi': 'Varanasi Spiritual',
        'mumbai': 'Mumbai Night Life',
        'rishikesh': 'Rishikesh Yoga',
        'tirupathi': 'Tirupathi Spiritual Temple'
    }
    
    def __init__(self):
        """Set up the parser with empty state"""
        self.user_input = ""
        self.parsed_filters = {}
        self._term_cache = {}  # Performance optimization for tokenization
    
    def _isolate_search_tokens(self) -> None:
        """
        Pull out significant words from user input for content matching.
        
        Filters out filler words and keeps only substantive terms.
        Enables matching against destination content, not just predefined categories.
        """
        filler_words = {
            'a', 'an', 'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
            'of', 'with', 'from', 'by', 'as', 'is', 'are', 'have', 'has', 'be',
            'can', 'i', 'you', 'we', 'they', 'what', 'where', 'when', 'why', 'how',
            'please', 'find', 'show', 'get', 'give', 'tell', 'me', 'my', 'want',
            # Budget-related words that shouldn't be search terms
            'budget', 'rupees', 'rs', 'inr', 'price', 'cost', 'under', 'upto', 'between',
            # Duration-related words
            'days', 'day', 'week', 'weeks', 'month', 'months',
            # Distance-related words  
            'km', 'kilometers', 'distance', 'away', 'far', 'near', 'within'
        }
        
        # Break input into individual words
        word_list = self.user_input.split()
        
        # Keep only meaningful words (not filler, length > 2, not numbers)
        significant_words = [
            word.strip('.,!?;:') for word in word_list 
            if (word.lower() not in filler_words and 
                len(word) > 2 and 
                not word.isdigit())  # Exclude pure numbers like "3000"
        ]
        
        self.parsed_filters['query_terms'] = significant_words
    
    def _identify_destination(self) -> None:
        """
        Detect specific location mentions in the user's request.
        
        Scans for recognized destination names and maps them to canonical forms.
        """
        for alias, canonical_name in self.DESTINATION_ALIASES.items():
            if alias in self.user_input.lower():
                self.parsed_filters['place_name'] = canonical_name
                return
    
    def _parse_timing_preferences(self) -> None:
        """Identify preferred travel months or seasons from user input"""
        timing_map = {
            'january': 'january',
            'february': 'february',
            'march': 'march',
            'april': 'april',
            'may': 'may',
            'june': 'june',
            'july': 'july',
            'august': 'august',
            'september': 'september',
            'october': 'october',
            'november': 'november',
            'december': 'december',
            'winter': ['december', 'january', 'february'],
            'summer': ['march', 'april', 'may', 'june'],
            'monsoon': ['june', 'july', 'august', 'september'],
            'autumn': ['september', 'october', 'november'],
            'season': None  # Generic season indicator
        }
        
        detected_months = []
        for timing_key, timing_value in timing_map.items():
            if timing_key in self.user_input:
                if isinstance(timing_value, list):
                    detected_months.extend(timing_value)
                elif timing_value is not None:
                    detected_months.append(timing_value)
                # Generic 'season' doesn't add specific months
        
        if detected_months:
            self.parsed_filters['best_months'] = list(set(detected_months))  # Deduplicate

    
    def process_query(self, query: str) -> Dict:
        """
        Transform raw text query into organized search parameters.
        
        Analyzes natural language input and builds structured filter dictionary
        covering destination, finances, vibes, trip duration, distance, and timing.
        
        Args:
            query: User's search text
            
        Returns:
            Dictionary with parsed parameters:
            - budget_max: Upper financial limit (int or None)
            - mood: Atmosphere/vibe preferences (list)
            - duration_days: Length of trip (int or None)
            - distance_km: Maximum travel distance (int or None)
            - place_name: Specific destination if mentioned (str or None)
            - best_months: Preferred travel months (list)
            
        Raises:
            TypeError: If input is not text
        """
        if not isinstance(query, str):
            raise TypeError(f"Input must be text, received {type(query).__name__}")
            
        self.user_input = query.lower().strip()
        
        # Set up empty filter structure with correct data types
        self.parsed_filters = {
            'budget_min': None,  # Lower financial bound
            'budget_max': None,
            'mood': [],
            'duration_days': None,
            'distance_km': None,
            'place_name': None,
            'best_months': [],
            'query_terms': []
        }
        
        # Run all extraction methods
        self._isolate_search_tokens()
        self._identify_destination()
        self._parse_financial_limits()
        self._detect_atmosphere()
        self._parse_timing_preferences()
        self._parse_trip_length()
        self._parse_travel_range()
        
        return self.parsed_filters
    
    def _parse_financial_limits(self) -> None:
        """
        Extract budget information from user query.
        
        Handles:
        - Ranges: "1000-2000", "budget is 1000-2000", "1000 to 2000"
        - Upper limits: "budget 1500", "under 2000"
        - Keywords: "cheap" -> 3500
        """
        if not self.user_input:
            return
            
        # Priority 1: Look for budget RANGES first
        # Must check ranges before single values
        range_regex_list = [
            r'(\d+)\s*-\s*(\d+)',                          # 1000-2000
            r'(\d+)\s+to\s+(\d+)',                         # 1000 to 2000
            r'between\s+(\d+)\s+and\s+(\d+)',              # between 1000 and 2000
            r'from\s+(\d+)\s+to\s+(\d+)'                   # from 1000 to 2000
        ]
        
        for regex_pattern in range_regex_list:
            range_match = re.search(regex_pattern, self.user_input)
            if range_match:
                try:
                    lower_bound = int(range_match.group(1))
                    upper_bound = int(range_match.group(2))
                    # Swap if reversed
                    if lower_bound > upper_bound:
                        lower_bound, upper_bound = upper_bound, lower_bound
                        
                    self.parsed_filters['budget_min'] = lower_bound
                    self.parsed_filters['budget_max'] = upper_bound
                    return # Range found, exit
                except ValueError:
                    continue

        # Priority 2: Look for SINGLE values (upper limit)
        # Only if no range detected
        single_value_patterns = [
            r'(?:budget|rupees|rs|inr)\s*(?:is|of|max|maximum|limit|under|below)?\s*[:\s]*(\d+)',
            r'(\d+)\s*(?:rupees|rs|inr)',
            r'(?:upto|up to|within|max|maximum)\s+(?:rupees|rs)?\s*[:\s]*(\d+)',
            r'^(\d+)$',
        ]
        
        for single_pattern in single_value_patterns:
            single_match = re.search(single_pattern, self.user_input)
            if single_match:
                try:
                    amount_str = single_match.group(1)
                    self.parsed_filters['budget_max'] = int(amount_str)
                    return  # Value found, exit
                except ValueError:
                    continue
        
        # Priority 3: Check for budget keywords with default values
        if 'cheap' in self.user_input or 'affordable' in self.user_input or 'budget' in self.user_input or 'friendly' in self.user_input:
            self.parsed_filters['budget_max'] = 3500  # Default economical limit
    
    def _detect_atmosphere(self) -> None:
        """
        Identify vibe/atmosphere preferences from user text.
        
        Scans for atmosphere keywords and builds list of matching vibes.
        Leverages expanded keyword catalog for improved matching.
        """
        detected_vibes = set()
        
        for vibe_category, keyword_list in self.VIBE_LEXICON.items():
            for keyword in keyword_list:
                if keyword in self.user_input.lower():
                    detected_vibes.add(vibe_category)
                    break  # Move to next vibe category
        
        self.parsed_filters['mood'] = list(detected_vibes) if detected_vibes else []
    
    def _parse_trip_length(self) -> None:
        """Extract trip duration from user input"""
        duration_patterns = [
            r'(\d+)\s*(?:days?|d)',
            r'(?:for|duration)[\s:]*(\d+)\s*days?'
        ]
        
        for duration_regex in duration_patterns:
            duration_match = re.search(duration_regex, self.user_input)
            if duration_match:
                self.parsed_filters['duration_days'] = int(duration_match.group(1))
                break
    
    def _parse_travel_range(self) -> None:
        """Extract maximum travel distance from user input"""
        distance_patterns = [
            r'(?:within|upto|up to|max|maximum|km)[\s:]*(\d+)\s*km',
            r'(\d+)\s*km',
        ]
        
        for distance_regex in distance_patterns:
            distance_match = re.search(distance_regex, self.user_input)
            if distance_match:
                self.parsed_filters['distance_km'] = int(distance_match.group(1))
                break
    
    def get_constraints(self) -> Dict:
        """Retrieve the parsed filter dictionary"""
        return self.parsed_filters
