"""
Query Processor: Parses user queries and extracts structured constraints

Converts natural language user queries into structured search constraints
that can be used by the ranking system to find relevant travel spots.

Features:
- Place name extraction
- Budget amount parsing
- Mood keyword detection
- Duration extraction
- Distance constraint parsing
- Best months identification
"""
from typing import Dict, List
import re


class QueryProcessor:
    """
    Processes natural language queries from users.
    Extracts budget, mood, duration, distance, and location constraints.
    """
    
    # Mood keywords mapping - organized by category
    MOOD_KEYWORDS = {
        'adventure': ['adventure', 'trekking', 'hiking', 'extreme', 'thrill', 'trek', 'climb'],
        'nature': ['nature', 'wildlife', 'forest', 'scenic', 'landscape', 'hill', 'mountain', 'snow'],
        'relaxing': ['relax', 'chill', 'peaceful', 'calm', 'quiet', 'rest', 'beach', 'backwater'],
        'party': ['party', 'nightlife', 'disco', 'club', 'fun', 'dance', 'night'],
        'cultural': ['culture', 'cultural', 'heritage', 'art', 'museum', 'city', 'tour'],
        'history': ['history', 'historical', 'ancient', 'monument', 'temple'],
        'spiritual': ['spiritual', 'meditation', 'yoga', 'zen', 'peace'],
        'romantic': ['romantic', 'couple', 'honeymoon', 'love']
    }
    
    # Place name mappings for common queries
    PLACE_NAME_MAPPINGS = {
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
        """Initialize the query processor"""
        self.query = ""
        self.constraints = {}
        self._tokenize_cache = {}  # Cache tokenized results
    
    def _extract_query_terms(self) -> None:
        """
        Extract raw query terms for full-text searching across descriptions.
        
        Removes common stop words and extracts meaningful terms from the query.
        This allows searching destinations by their full descriptions, not just
        specific categories.
        """
        stop_words = {
            'a', 'an', 'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
            'of', 'with', 'from', 'by', 'as', 'is', 'are', 'have', 'has', 'be',
            'can', 'i', 'you', 'we', 'they', 'what', 'where', 'when', 'why', 'how',
            'please', 'find', 'show', 'get', 'give', 'tell', 'me', 'my', 'want'
        }
        
        # Split query into terms
        terms = self.query.split()
        
        # Filter stop words and extract meaningful terms
        meaningful_terms = [
            term.strip('.,!?;:') for term in terms 
            if term.lower() not in stop_words and len(term) > 2
        ]
        
        self.constraints['query_terms'] = meaningful_terms
    
    def _extract_place_name(self) -> None:
        """
        Extract place name from query.
        
        Checks for known place names in the query and extracts them.
        """
        for key, place in self.PLACE_NAME_MAPPINGS.items():
            if key in self.query.lower():
                self.constraints['place_name'] = place
                return
    
    def _extract_months(self) -> None:
        """Extract best visit months/season from query"""
        months = {
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
            'season': None  # Trigger any season match
        }
        
        months_found = []
        for key, value in months.items():
            if key in self.query:
                if isinstance(value, list):
                    months_found.extend(value)
                elif value is not None:
                    months_found.append(value)
                # 'season' keyword alone doesn't add specific months
        
        if months_found:
            self.constraints['best_months'] = list(set(months_found))  # Remove duplicates

    
    def process_query(self, query: str) -> Dict:
        """
        Parse query string and extract all constraints.
        
        Processes a natural language query and extracts structured constraints
        for place name, budget, mood, duration, distance, and best months.
        
        Args:
            query: Natural language query string
            
        Returns:
            Dictionary of extracted constraints with keys:
            - budget_max: Maximum budget in rupees (int or None)
            - mood: List of mood preferences
            - duration_days: Trip duration in days (int or None)
            - distance_km: Maximum distance in km (int or None)
            - place_name: Specific place if mentioned (str or None)
            - best_months: List of preferred months
            
        Raises:
            TypeError: If query is not a string
        """
        if not isinstance(query, str):
            raise TypeError(f"Query must be a string, got {type(query).__name__}")
            
        self.query = query.lower().strip()
        
        # Initialize constraints with proper types
        self.constraints = {
            'budget_max': None,
            'mood': [],
            'duration_days': None,
            'distance_km': None,
            'place_name': None,
            'best_months': [],
            'query_terms': []  # NEW: Raw query terms for description matching
        }
        
        # Extract all constraints from query
        self._extract_query_terms()  # NEW: Extract terms first
        self._extract_place_name()
        self._extract_budget()
        self._extract_mood()
        self._extract_months()
        self._extract_duration()
        self._extract_distance()
        
        return self.constraints
    
    def _extract_budget(self) -> None:
        """
        Extract budget constraint from query.
        
        Supports multiple formats:
        - "1000" - just a number
        - "budget 1000"
        - "1000 rupees"
        - "I have 1000 rupees"
        - "cheap" / "budget-friendly" -> 3500 default
        
        Always extract actual numbers first (highest priority) before applying defaults.
        """
        if not self.query:
            return
            
        # Try to extract actual budget numbers first (highest priority)
        patterns = [
            r'(?:budget|rupees|rs|inr)\s*[:\s]+(\d+)',  # budget: 5000 or rupees 5000
            r'(\d+)\s*(?:rupees|rs|inr)',                # 5000 rupees
            r'(?:upto|up to|within|max|maximum)\s+(?:rupees|rs)?\s*[:\s]*(\d+)',  # upto 5000
            r'^(\d+)$',                                   # just "5000"
        ]
        
        for pattern in patterns:
            match = re.search(pattern, self.query)
            if match:
                try:
                    budget_str = match.group(1)
                    self.constraints['budget_max'] = int(budget_str)
                    return  # Found actual number, don't apply defaults
                except ValueError:
                    continue
        
        # If no number found, check for budget-related keywords with defaults
        if 'cheap' in self.query or 'affordable' in self.query or 'budget' in self.query or 'friendly' in self.query:
            self.constraints['budget_max'] = 3500  # Default affordable budget
    
    def _extract_mood(self) -> None:
        """
        Extract mood constraints from query.
        
        Searches for mood keywords and adds matching moods to constraints.
        Uses an enhanced keyword list for better destination matching.
        """
        moods_found = set()
        
        for mood, keywords in self.MOOD_KEYWORDS.items():
            for keyword in keywords:
                if keyword in self.query.lower():
                    moods_found.add(mood)
                    break  # Found this mood, move to next
        
        self.constraints['mood'] = list(moods_found) if moods_found else []
    
    def _extract_duration(self) -> None:
        """Extract duration constraint from query"""
        patterns = [
            r'(\d+)\s*(?:days?|d)',
            r'(?:for|duration)[\s:]*(\d+)\s*days?'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, self.query)
            if match:
                self.constraints['duration_days'] = int(match.group(1))
                break
    
    def _extract_distance(self) -> None:
        """Extract distance constraint from query"""
        patterns = [
            r'(?:within|upto|up to|max|maximum|km)[\s:]*(\d+)\s*km',
            r'(\d+)\s*km',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, self.query)
            if match:
                self.constraints['distance_km'] = int(match.group(1))
                break
    
    def get_constraints(self) -> Dict:
        """Return parsed constraints"""
        return self.constraints
