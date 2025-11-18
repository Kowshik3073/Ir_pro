"""
Query Processor: Parses user queries and converts them into structured constraints
"""
from typing import Dict, List, Tuple
import re


class QueryProcessor:
    """
    Processes natural language queries from users.
    Extracts budget, mood, duration, and distance constraints.
    """
    
    # Mood keywords mapping
    MOOD_KEYWORDS = {
        'adventure': ['adventure', 'trekking', 'hiking', 'extreme', 'thrill'],
        'nature': ['nature', 'wildlife', 'forest', 'scenic', 'landscape'],
        'relaxing': ['relax', 'chill', 'peaceful', 'calm', 'quiet', 'rest'],
        'party': ['party', 'nightlife', 'disco', 'club', 'fun', 'dance'],
        'cultural': ['culture', 'cultural', 'heritage', 'art', 'museum'],
        'history': ['history', 'historical', 'ancient', 'monument', 'temple'],
        'spiritual': ['spiritual', 'meditation', 'yoga', 'zen', 'peace'],
        'romantic': ['romantic', 'couple', 'honeymoon', 'love']
    }
    
    def __init__(self):
        self.query = ""
        self.constraints = {}
    
    def _extract_place_name(self) -> None:
        """Extract place name from query"""
        # List of known place names
        place_names = {
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
            'rishikesh': 'Rishikesh Yoga'
        }
        
        for key, place in place_names.items():
            if key in self.query:
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
        Parse query string and extract constraints.
        
        Example queries:
        - "manali" -> searches for Manali destination
        - "beach november" -> beach mood with best months = november
        - "I have 5000 rupees, want adventure for 4 days within 1000km"
        - "Budget 3000, mood: relaxing, 2 days"
        """
        self.query = query.lower()
        self.constraints = {
            'budget_max': None,
            'mood': [],
            'duration_days': None,
            'distance_km': None,
            'place_name': None,
            'best_months': []
        }
        
        self._extract_place_name()
        self._extract_budget()
        self._extract_mood()
        self._extract_months()
        self._extract_duration()
        self._extract_distance()
        
        return self.constraints
    
    def _extract_budget(self) -> None:
        """Extract budget constraint from query"""
        # Check for "cheap" keyword first
        if 'cheap' in self.query or 'budget' in self.query or 'afford' in self.query:
            # For cheap/budget queries, set max to 3500 (affordable range)
            self.constraints['budget_max'] = 3500
            return
        
        # Patterns: "5000", "budget 5000", "rupees 5000", etc.
        patterns = [
            r'(?:budget|rupees|rs|inr)[\s:]+(\d+)',
            r'(\d+)\s*(?:rupees|rs|inr)',
            r'(?:upto|up to|within|max|maximum)\s+(?:rupees|rs)?[\s:]*(\d+)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, self.query)
            if match:
                self.constraints['budget_max'] = int(match.group(1))
                break
    
    def _extract_mood(self) -> None:
        """Extract mood constraints from query"""
        moods_found = set()
        
        # Add keywords for better destination matching
        enhanced_keywords = {
            'adventure': ['adventure', 'trekking', 'hiking', 'extreme', 'thrill', 'trek', 'climb'],
            'nature': ['nature', 'wildlife', 'forest', 'scenic', 'landscape', 'hill', 'mountain', 'snow'],
            'relaxing': ['relax', 'chill', 'peaceful', 'calm', 'quiet', 'rest', 'beach', 'backwater'],
            'party': ['party', 'nightlife', 'disco', 'club', 'fun', 'dance', 'night'],
            'cultural': ['culture', 'cultural', 'heritage', 'art', 'museum', 'city', 'tour'],
            'history': ['history', 'historical', 'ancient', 'monument', 'temple'],
            'spiritual': ['spiritual', 'meditation', 'yoga', 'zen', 'peace'],
            'romantic': ['romantic', 'couple', 'honeymoon', 'love']
        }
        
        for mood, keywords in enhanced_keywords.items():
            for keyword in keywords:
                if keyword in self.query:
                    moods_found.add(mood)
        
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
