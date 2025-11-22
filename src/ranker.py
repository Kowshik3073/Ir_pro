"""
ScoringEngine Module: Implements relevance computation and retrieval algorithms
Utilizes TF-IDF and filter-based matching for destination relevance scoring
"""
import logging
import math
from typing import Dict, List, Tuple, Optional
from src.indexer import TravelSpotIndexer

logger = logging.getLogger(__name__)


class TravelSpotRanker:
    """
    Computes relevance scores for destinations based on user criteria.
    Combines filter satisfaction with relevance weighting
    """
    
    def __init__(self, indexer: TravelSpotIndexer):
        self.data_indexer = indexer
    
    def rank_spots(self, constraints: Dict, top_k: int = 5) -> List[Tuple[int, float, Dict]]:
        """
        Compute relevance scores for all destinations based on user criteria.
        
        Returns all meaningful results (score > threshold) independent of top_k.
        Excludes low-relevance results even if count is below top_k.
        
        Args:
            constraints: Parsed user filter criteria dictionary
            top_k: Suggested result count (used as guidance, not strict limit)
            
        Returns:
            List of (destination_id, relevance_score, metadata) tuples ordered by score descending
            
        Raises:
            ValueError: If top_k is below 1
        """
        if top_k < 1:
            raise ValueError("top_k value must be at least 1")
            
        # Minimum relevance threshold: Only display results with substantial relevance
        # 0.4 = 40% relevance (calibrated for weighted scoring approach)
        MIN_RELEVANCE_THRESHOLD = 0.4
        
        relevance_scores = {}
        
        for destination_id, destination_data in self.data_indexer.destination_info.items():
            computed_score = self._compute_destination_relevance(destination_id, destination_data, constraints)
            relevance_scores[destination_id] = computed_score
        
        # Order by score (descending), use rating as tiebreaker
        sorted_results = sorted(relevance_scores.items(), 
                       key=lambda item: (item[1], self.data_indexer.get_spot_by_id(item[0])['rating']),
                       reverse=True)
        
        final_results = []
        for destination_id, relevance_score in sorted_results:
            # Apply relevance threshold, not top_k limit
            if relevance_score < MIN_RELEVANCE_THRESHOLD:
                break  # Remaining items will have lower scores
                
            destination_data = self.data_indexer.get_spot_by_id(destination_id)
            if destination_data:
                final_results.append((destination_id, relevance_score, destination_data))
        
        logger.debug(f"Scored {len(final_results)} destinations with relevance >= {MIN_RELEVANCE_THRESHOLD}")
        return final_results
    
    def _compute_destination_relevance(self, spot_id: int, metadata: Dict, constraints: Dict) -> float:
        """
        Calculate overall relevance score for a destination.
        
        ADAPTIVE WEIGHTING: Weights adjust based on explicit user criteria.
        When trip length is explicitly mentioned, it becomes PRIMARY (20%).
        
        Scoring components:
        - Content match in details (15%): Textual relevance
        - Financial fit (25%): Critical for user satisfaction  
        - Atmosphere match (20%): User preference alignment
        - Trip length (20%): CRITICAL when explicitly specified
        - Destination category (12%): Ensures correct type
        - Timing preferences (5%): Travel planning
        - Travel range (3%): Accessibility factor
        """
        total_score = 0.0
        
        # Detect if trip length was explicitly mentioned (high priority signal)
        trip_length_explicit = constraints.get('duration_days') is not None
        
        # Component 0: CONTENT/DESCRIPTION MATCHING (15% weight)
        if constraints.get('query_terms'):
            content_relevance = self._evaluate_content_match(metadata, constraints['query_terms'])
            
            # SMART FILTERING: Detect if query contains location/type keywords
            # These MUST match the destination, unlike mood keywords
            location_type_keywords = {
                'mountain', 'mountains', 'hill', 'hills', 'beach', 'beaches', 
                'desert', 'island', 'islands', 'valley', 'lake', 'backwater', 
                'backwaters', 'forest', 'jungle', 'snow', 'temple', 'palace',
                'fort', 'city', 'village', 'waterfall', 'river', 'sea', 'ocean'
            }
            
            # Check if any query term is a location/type keyword
            has_location_keyword = any(
                term.lower() in location_type_keywords 
                for term in constraints['query_terms']
            )
            
            # If location keyword present but no strong match, filter out
            # This ensures "mountain budget 5000" only shows mountains
            # But "adventure budget 5000" can match via mood
            if has_location_keyword and content_relevance < 0.5:
                return 0.0  # Location keyword doesn't match - filter out
            
            total_score += content_relevance * 0.15
        else:
            total_score += 0.5 * 0.15
        
        # Component 1: FINANCIAL FIT SCORE (25% weight) - Always primary
        if constraints.get('budget_max'):
            # OVERLAP FILTERING: Display destinations with ANY overlap with user's financial range
            if constraints.get('budget_min'):
                # Verify ANY overlap between ranges
                # No overlap if: destination_max < user_min OR destination_min > user_max
                if metadata['budget_max'] < constraints['budget_min']:
                    return 0.0  # Destination entirely too economical
                if metadata['budget_min'] > constraints['budget_max']:
                    return 0.0  # Destination entirely too expensive
                # Overlap exists - include it!
            else:
                # Only max specified: destination must start at or below user's max
                if metadata['budget_min'] > constraints['budget_max']:
                    return 0.0

            financial_relevance = self._evaluate_financial_fit(
                metadata['budget_min'],
                metadata['budget_max'],
                constraints['budget_max'],
                constraints.get('budget_min')
            )
            total_score += financial_relevance * 0.25
        else:
            total_score += 0.5 * 0.25
        
        # Component 2: ATMOSPHERE SCORE (20% weight)
        if constraints.get('mood'):
            atmosphere_relevance = self._evaluate_atmosphere_match(metadata['mood'], constraints['mood'])
            total_score += atmosphere_relevance * 0.20
        else:
            total_score += 0.5 * 0.20
        
        # Component 3: Trip Length Score (20% weight) - BOOSTED when explicitly specified
        # Trip length is a hard constraint when mentioned in query
        if trip_length_explicit:
            trip_length_relevance = self._evaluate_trip_length_fit(
                metadata['duration_days'],
                constraints['duration_days']
            )
            total_score += trip_length_relevance * 0.20
        else:
            total_score += 0.5 * 0.20
        
        # Component 4: Destination Category Boost (12% weight)
        category_relevance = self._evaluate_category_boost(metadata['name'], constraints)
        total_score += category_relevance * 0.12
        
        # Component 5: Timing Preferences Match (5% weight)
        if constraints.get('best_months'):
            timing_relevance = self._evaluate_timing_match(
                metadata.get('best_months', []),
                constraints['best_months']
            )
            total_score += timing_relevance * 0.05
        else:
            total_score += 0.5 * 0.05
        
        # Component 6: Travel Range Score (3% weight)
        if constraints.get('distance_km'):
            range_relevance = self._evaluate_travel_range(
                metadata['distance_km'],
                constraints['distance_km']
            )
            total_score += range_relevance * 0.03
        else:
            total_score += 0.5 * 0.03
        
        return total_score
    
    def _evaluate_content_match(self, metadata: Dict, query_terms: List[str]) -> float:
        """
        Score based on how well search terms match the details, title, and atmosphere.
        
        STRICT MATCHING:
        - If search term in title: High score (1.0)
        - If search term NOT in title but in details/atmosphere: Low score (0.3)
        - If no match: Score 0
        
        Ensures "beach" returns only "Goa Beach", not all destinations mentioning beach.
        """
        if not query_terms:
            return 0.5
        
        title_lowercase = metadata['name'].lower()
        details_lowercase = metadata.get('description', '').lower()
        atmosphere_text = ' '.join(metadata.get('mood', [])).lower()
        
        title_hits = 0
        details_hits = 0
        atmosphere_hits = 0
        total_terms = len(query_terms)
        
        for search_term in query_terms:
            term_lowercase = search_term.lower()
            
            if term_lowercase in title_lowercase:
                title_hits += 1
            elif term_lowercase in atmosphere_text:
                atmosphere_hits += 1
            elif term_lowercase in details_lowercase:
                details_hits += 1
        
        # STRICT SCORING:
        # If ANY term matches title, highly relevant
        if title_hits > 0:
            # Perfect match if all terms in title
            return min(title_hits / total_terms, 1.0)
        
        # Mood/atmosphere match is STRONG (not weak) - these are primary categorizations
        # Example: "spiritual" matching mood=['spiritual'] should score high
        if atmosphere_hits > 0:
            return 0.8 * (atmosphere_hits / total_terms)  # Changed from 0.3 to 0.8
        
        # Description match is weaker - prevents false positives
        # Example: "beach" in "hill station with beach views" description
        if details_hits > 0:
            return 0.2 * (details_hits / total_terms)
        
        # No match at all
        return 0
    
    def _evaluate_category_boost(self, spot_name: str, constraints: Dict) -> float:
        """
        Boost score if destination title contains tourism/destination keywords.
        
        Ensures proper destination category matching. Lower weight (20%) than
        financial/atmosphere since title is mostly for categorization.
        """
        title_lowercase = spot_name.lower()
        
        # TIER 1: PRIMARY DESTINATION CATEGORIES - HIGH BOOST (0.9)
        primary_keywords = ['beach', 'backwater', 'spiritual', 'devotion']
        for keyword in primary_keywords:
            if keyword in title_lowercase:
                return 0.9
        
        # TIER 2: SECONDARY DESTINATION CATEGORIES (0.85)
        secondary_keywords = ['hill', 'mountain', 'snow', 'leh', 'ladakh', 'yoga']
        for keyword in secondary_keywords:
            if keyword in title_lowercase:
                return 0.85
        
        # TIER 3: SPECIALTY KEYWORDS (0.75)
        specialty_keywords = ['night', 'life', 'city', 'tour']
        for keyword in specialty_keywords:
            if keyword in title_lowercase:
                return 0.75
        
        # DEFAULT: Generic title (0.5)
        # Don't heavily penalize titles without keywords
        return 0.5
    
    def _evaluate_timing_match(self, spot_best_months: List[str], user_months: List[str]) -> float:
        """
        Score based on optimal travel timing/season match.
        If user specifies preferred timing or season, verify match with destination's optimal periods.
        
        Supports: winter, summer, monsoon, autumn, and specific months
        """
        if not user_months or not spot_best_months:
            return 0.5  # Default if no timing specified
        
        # Count overlapping months
        overlap_count = sum(1 for month in user_months if month in spot_best_months)
        return min(1.0, overlap_count / len(user_months))  # Cap at 1.0
    
    def _evaluate_financial_fit(self, budget_min: int, budget_max: int, user_budget_max: int, user_budget_min: Optional[int] = None) -> float:
        """
        Score based on financial compatibility.
        
        Args:
            budget_min: Destination's minimum cost
            budget_max: Destination's maximum cost
            user_budget_max: User's maximum budget
            user_budget_min: User's minimum budget (optional)
        """
        # Scenario 1: Range Query (e.g. 1000-2000)
        if user_budget_min is not None:
            # Check for overlap between [user_min, user_max] and [destination_min, destination_max]
            overlap_lower = max(budget_min, user_budget_min)
            overlap_upper = min(budget_max, user_budget_max)
            
            if overlap_lower <= overlap_upper:
                # Overlap exists!
                # Calculate coverage of destination's range by user's range
                # or just return high score for overlap.
                return 1.0
            else:
                # No overlap, but we already filtered strictly invalid ones.
                # This shouldn't be reached if strict filtering is on, 
                # but just in case:
                return 0.5

        # Scenario 2: Max Limit Query (e.g. budget 2000)
        if budget_min <= user_budget_max <= budget_max:
            # User budget within destination's range
            # BONUS: Prioritize destinations with LOWEST budget_min (most affordable)
            affordability_bonus = max(0, 1.0 - (budget_min / user_budget_max) * 0.1)
            return min(1.0, 1.0 + affordability_bonus)
        elif user_budget_max < budget_min:
            # User budget too low - penalize significantly
            # (Should be filtered by strict check, but keeping for robustness)
            return 0.0
        else:
            # User budget higher than needed (user_budget_max > budget_max)
            # This is GOOD! User can easily afford this.
            return 1.0
    
    def _evaluate_atmosphere_match(self, spot_moods: List[str], user_moods: List[str]) -> float:
        """
        Score based on atmosphere match.
        Score = (matching atmospheres) / (total user atmospheres requested)
        """
        if not user_moods:
            return 1.0
        
        overlap_count = sum(1 for mood in user_moods if mood in spot_moods)
        return overlap_count / len(user_moods)
    
    def _evaluate_trip_length_fit(self, spot_duration: int, user_duration: int) -> float:
        """
        Score based on trip length compatibility.
        
        CRITICAL: Heavily reward exact matches and penalize mismatches.
        When user specifies trip length, it's a PRIMARY hard constraint.
        
        Scoring strategy:
        - Exact match (diff=0): 1.0 (perfect)
        - Off by 1 day: 0.90
        - Off by 2 days: 0.75  
        - Off by 3 days: 0.55
        - Beyond 3 days: very poor score (~0.30-0.40)
        
        Ensures exact matches always win over close mismatches.
        """
        difference = abs(spot_duration - user_duration)
        
        if difference == 0:
            return 1.0  # Exact match - highest score
        elif difference == 1:
            return 0.90  # Very close
        elif difference == 2:
            return 0.75  # Close but not ideal
        elif difference == 3:
            return 0.55  # Moderately different
        elif difference == 4:
            return 0.40  # Significantly different
        else:
            # Very large difference - heavy penalty
            return max(0.25, 1.0 - (difference * 0.12))
    
    def _evaluate_travel_range(self, spot_distance: int, max_distance: int) -> float:
        """
        Score based on travel distance.
        Score = 1.0 if within max distance, else penalize
        Prefer closer destinations within the limit
        """
        if spot_distance <= max_distance:
            # Prefer closer destinations: bonus for being within range
            proximity_bonus = 1.0 - (spot_distance / max_distance) * 0.3
            return min(1.0, proximity_bonus)
        else:
            # Beyond user's distance limit
            excess_distance = spot_distance - max_distance
            distance_penalty = min(excess_distance / max_distance, 0.5)
            return max(0.3, 1.0 - distance_penalty)
    
    def explain_score(self, spot_id: int, metadata: Dict, constraints: Dict) -> Dict:
        """
        Provide detailed breakdown of score components for a destination.
        
        Helps users understand why a destination was ranked in a certain position.
        """
        explanation_data = {
            'spot_id': spot_id,
            'spot_name': metadata['name'],
            'components': {}
        }
        
        # Financial fit (25% weight) - HIGHEST IMPACT
        if constraints.get('budget_max'):
            financial_score = self._evaluate_financial_fit(
                metadata['budget_min'],
                metadata['budget_max'],
                constraints['budget_max'],
                constraints.get('budget_min')
            )
            
            if constraints.get('budget_min'):
                reason_text = f"Budget ₹{metadata['budget_min']}-{metadata['budget_max']}, you want ₹{constraints['budget_min']}-{constraints['budget_max']}"
            else:
                reason_text = f"Budget ₹{metadata['budget_min']}-{metadata['budget_max']}, you have ₹{constraints['budget_max']}"
                
            explanation_data['components']['budget'] = {
                'score': round(financial_score * 0.25, 3),
                'reason': reason_text
            }
        else:
            explanation_data['components']['budget'] = {
                'score': round(0.5 * 0.25, 3),
                'reason': "No budget specified (default score)"
            }
        
        # Atmosphere (25% weight)
        if constraints.get('mood'):
            atmosphere_score = self._evaluate_atmosphere_match(metadata['mood'], constraints['mood'])
            explanation_data['components']['mood'] = {
                'score': round(atmosphere_score * 0.25, 3),
                'reason': f"Moods: {metadata['mood']}, you want: {constraints['mood']}"
            }
        else:
            explanation_data['components']['mood'] = {
                'score': round(0.5 * 0.25, 3),
                'reason': "No mood specified (default score)"
            }
        
        # Destination Category (20% weight)
        category_boost = self._evaluate_category_boost(metadata['name'], constraints)
        explanation_data['components']['destination_type'] = {
            'score': round(category_boost * 0.20, 3),
            'reason': f"Destination type: '{metadata['name']}' (boost: {category_boost})"
        }
        
        # Timing Preferences (15% weight)
        if constraints.get('best_months'):
            timing_boost = self._evaluate_timing_match(
                metadata.get('best_months', []),
                constraints['best_months']
            )
            explanation_data['components']['best_months'] = {
                'score': round(timing_boost * 0.15, 3),
                'reason': f"Best months: {metadata.get('best_months', [])}, you prefer: {constraints['best_months']}"
            }
        else:
            explanation_data['components']['best_months'] = {
                'score': round(0.5 * 0.15, 3),
                'reason': "No months specified (default score)"
            }
        
        # Trip Length (10% weight)
        if constraints.get('duration_days'):
            trip_length_score = self._evaluate_trip_length_fit(
                metadata['duration_days'],
                constraints['duration_days']
            )
            explanation_data['components']['duration'] = {
                'score': round(trip_length_score * 0.10, 3),
                'reason': f"Duration {metadata['duration_days']} days, you have {constraints['duration_days']} days"
            }
        else:
            explanation_data['components']['duration'] = {
                'score': round(0.5 * 0.10, 3),
                'reason': "No duration specified (default score)"
            }
        
        # Travel Range (5% weight)
        if constraints.get('distance_km'):
            range_score = self._evaluate_travel_range(
                metadata['distance_km'],
                constraints['distance_km']
            )
            explanation_data['components']['distance'] = {
                'score': round(range_score * 0.05, 3),
                'reason': f"Distance {metadata['distance_km']}km, your limit {constraints['distance_km']}km"
            }
        else:
            explanation_data['components']['distance'] = {
                'score': round(0.5 * 0.05, 3),
                'reason': "No distance specified (default score)"
            }
        
        return explanation_data
