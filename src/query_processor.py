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
        'tirupathi': 'tirupathi'
    }
    
    def __init__(self):
        """Initialize the query processor"""
        self.query = ""
        self.constraints = {}
    
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
        """Extract best visit months from query"""
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
            'autumn': ['september', 'october', 'november']
        }
        
        months_found = []
        for key, value in months.items():
            if key in self.query:
                if isinstance(value, list):
                    months_found.extend(value)
                else:
                    months_found.append(value)
        
        if months_found:
            self.constraints['best_months'] = list(set(months_found))  # Remove duplicates

    
    def process_query(self, query: str) -> Dict:
        """
        Parse query string and extract all constraints.
        
        Processes a natural language query and extracts structured constraints
        for place name, budget, mood, duration, distance, and best months.
        
        Example queries:
        - "manali" -> searches for Manali destination
        - "beach november" -> beach mood with best months = november
        - "I have 5000 rupees, want adventure for 4 days within 1000km"
        - "Budget 3000, mood: relaxing, 2 days"
        
        Args:
            query: Natural language query string
            
        Returns:
            Dictionary of extracted constraints with keys:
            - budget_max: Maximum budget in rupees
            - mood: List of mood preferences
            - duration_days: Trip duration in days
            - distance_km: Maximum distance in km
            - place_name: Specific place if mentioned
            - best_months: List of preferred months
        """
        self.query = query.lower().strip()
        self.constraints = {
            'budget_max': None,
            'mood': [],
            'duration_days': None,
            'distance_km': None,
            'place_name': None,
            'best_months': []
        }
        
        # Extract all constraints from query
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
        
        CRITICAL: Extract actual numbers FIRST before applying defaults
        """
        # Try to extract actual budget numbers first (highest priority)
        patterns = [
            r'(?:budget|rupees|rs|inr)[\s:]+(\d+)',  # budget: 5000 or rupees 5000
            r'(\d+)\s*(?:rupees|rs|inr)',              # 5000 rupees
            r'(?:upto|up to|within|max|maximum)\s+(?:rupees|rs)?[\s:]*(\d+)',  # upto 5000
            r'^(\d+)$',                                 # just "5000"
        ]
        
        for pattern in patterns:
            match = re.search(pattern, self.query)
            if match:
                self.constraints['budget_max'] = int(match.group(1))
                return  # Found actual number, don't apply defaults
        
        # If no number found, check for budget-related keywords with defaults
        if 'cheap' in self.query or 'afford' in self.query:
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
