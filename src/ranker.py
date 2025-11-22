"""
Ranker Module: Implements ranking and retrieval algorithms
Uses TF-IDF and constraint-based filtering for relevance ranking
"""
import logging
import math
from typing import Dict, List, Tuple, Optional
from src.indexer import TravelSpotIndexer

logger = logging.getLogger(__name__)


class TravelSpotRanker:
    """
    Ranks travel spots based on query constraints.
    Uses combined scoring: constraint satisfaction + relevance score
    """
    
    def __init__(self, indexer: TravelSpotIndexer):
        self.indexer = indexer
    
    def rank_spots(self, constraints: Dict, top_k: int = 5) -> List[Tuple[int, float, Dict]]:
        """
        Rank all travel spots based on constraints.
        
        Returns all relevant results (score > threshold) regardless of top_k.
        Filters out irrelevant results even if fewer than top_k.
        
        Args:
            constraints: Dictionary of parsed user constraints
            top_k: Suggested number of results (used as hint, not hard limit)
            
        Returns:
            List of (spot_id, score, metadata) tuples sorted by score descending
            
        Raises:
            ValueError: If top_k is less than 1
        """
        if top_k < 1:
            raise ValueError("top_k must be at least 1")
            
        # Relevance threshold: Only show results with meaningful relevance
        # 0.4 = 40% relevance score (adjusted for our weighted scoring)
        RELEVANCE_THRESHOLD = 0.4
        
        scores = {}
        
        for spot_id, metadata in self.indexer.spot_metadata.items():
            score = self._calculate_relevance_score(spot_id, metadata, constraints)
            scores[spot_id] = score
        
        # Sort by score (descending), then by rating as tiebreaker
        ranked = sorted(scores.items(), 
                       key=lambda x: (x[1], self.indexer.get_spot_by_id(x[0])['rating']),
                       reverse=True)
        
        results = []
        for spot_id, score in ranked:
            # Filter by relevance threshold, not by top_k
            if score < RELEVANCE_THRESHOLD:
                break  # Since sorted, all remaining will be lower
                
            metadata = self.indexer.get_spot_by_id(spot_id)
            if metadata:
                results.append((spot_id, score, metadata))
        
        logger.debug(f"Ranked {len(results)} spots with score >= {RELEVANCE_THRESHOLD}")
        return results
    
    def _calculate_relevance_score(self, spot_id: int, metadata: Dict, constraints: Dict) -> float:
        """
        Calculate relevance score for a spot.
        
        DYNAMIC WEIGHTING: Weights adapt based on explicit constraints.
        When duration is explicitly specified, it becomes PRIMARY (20%).
        
        Weighted factors:
        - Query match in description (15%): Content relevance
        - Budget (25%): Most important for user satisfaction  
        - Mood (20%): User preference matching
        - Duration (20%): CRITICAL when explicitly specified in query
        - Name/Destination type (12%): Ensures right category
        - Best months (5%): Travel planning
        - Distance (3%): Accessibility
        """
        score = 0.0
        
        # Check if duration is explicitly in the query (high priority signal)
        duration_specified = constraints.get('duration_days') is not None
        
        # 0. DESCRIPTION/CONTENT MATCHING (15% weight) - Reduced when duration is explicit
        # Search for query terms in description and name
        if constraints.get('query_terms'):
            desc_score = self._calculate_description_match_score(metadata, constraints['query_terms'])
            
            # STRICT FILTERING: If query terms provided but no strong match found
            # desc_score < 0.5 means no name match (only description/mood match)
            if desc_score < 0.5:
                # Check if any other explicit constraints exist
                has_other_constraints = (
                    constraints.get('budget_max') is not None or
                    constraints.get('mood') or
                    constraints.get('duration_days') is not None or
                    constraints.get('distance_km') is not None or
                    constraints.get('best_months')
                )
                
                # If no other constraints, this spot is irrelevant
                # User is searching by name/keyword only, so require name match
                if not has_other_constraints:
                    return 0.0
            
            score += desc_score * 0.15
        else:
            score += 0.5 * 0.15
        
        # 1. BUDGET SCORE (25% weight) - Always primary
        if constraints.get('budget_max'):
            # OVERLAP FILTERING: Show places with ANY overlap with user's budget range
            if constraints.get('budget_min'):
                # Check if there's ANY overlap between ranges
                # No overlap if: spot_max < user_min OR spot_min > user_max
                if metadata['budget_max'] < constraints['budget_min']:
                    return 0.0  # Spot is entirely too cheap
                if metadata['budget_min'] > constraints['budget_max']:
                    return 0.0  # Spot is entirely too expensive
                # Otherwise there's overlap - show it!
            else:
                # Only max specified: spot must start at or below user's max
                if metadata['budget_min'] > constraints['budget_max']:
                    return 0.0

            budget_score = self._calculate_budget_score(
                metadata['budget_min'],
                metadata['budget_max'],
                constraints['budget_max'],
                constraints.get('budget_min')
            )
            score += budget_score * 0.25
        else:
            score += 0.5 * 0.25
        
        # 2. MOOD SCORE (20% weight)
        if constraints.get('mood'):
            mood_score = self._calculate_mood_score(metadata['mood'], constraints['mood'])
            score += mood_score * 0.20
        else:
            score += 0.5 * 0.20
        
        # 3. Duration Score (20% weight) - BOOSTED when explicitly specified
        # Duration is a hard constraint when mentioned in query
        if duration_specified:
            duration_score = self._calculate_duration_score(
                metadata['duration_days'],
                constraints['duration_days']
            )
            score += duration_score * 0.20
        else:
            score += 0.5 * 0.20
        
        # 4. Place Name/Destination Type Boost (12% weight)
        name_boost = self._calculate_name_boost(metadata['name'], constraints)
        score += name_boost * 0.12
        
        # 5. Best Months Match (5% weight)
        if constraints.get('best_months'):
            months_boost = self._calculate_months_boost(
                metadata.get('best_months', []),
                constraints['best_months']
            )
            score += months_boost * 0.05
        else:
            score += 0.5 * 0.05
        
        # 6. Distance Score (3% weight)
        if constraints.get('distance_km'):
            distance_score = self._calculate_distance_score(
                metadata['distance_km'],
                constraints['distance_km']
            )
            score += distance_score * 0.03
        else:
            score += 0.5 * 0.03
        
        return score
    
    def _calculate_description_match_score(self, metadata: Dict, query_terms: List[str]) -> float:
        """
        Score based on how well query terms match the description, name, and mood.
        
        STRICT MATCHING:
        - If query term is in the name: Score highly (1.0)
        - If query term is NOT in name but in description/mood: Score low (0.3)
        - If no match at all: Score 0
        
        This ensures "beach" returns only "Goa Beach", not all places mentioning beach.
        """
        if not query_terms:
            return 0.5
        
        name_lower = metadata['name'].lower()
        desc_lower = metadata.get('description', '').lower()
        moods_text = ' '.join(metadata.get('mood', [])).lower()
        
        name_matches = 0
        desc_matches = 0
        mood_matches = 0
        total_terms = len(query_terms)
        
        for term in query_terms:
            term_lower = term.lower()
            
            if term_lower in name_lower:
                name_matches += 1
            elif term_lower in moods_text:
                mood_matches += 1
            elif term_lower in desc_lower:
                desc_matches += 1
        
        # STRICT SCORING:
        # If ANY term matches the name, this is highly relevant
        if name_matches > 0:
            # Perfect match if all terms in name
            return min(name_matches / total_terms, 1.0)
        
        # If no name match but mood/description match, give low score
        # This prevents "beach" from matching "hill station with beach views"
        if mood_matches > 0:
            return 0.3 * (mood_matches / total_terms)
        
        if desc_matches > 0:
            return 0.2 * (desc_matches / total_terms)
        
        # No match at all
        return 0
    
    def _calculate_name_boost(self, spot_name: str, constraints: Dict) -> float:
        """
        Boost score if spot name contains tourism/destination keywords.
        
        Ensures proper destination type matching. Lower weight (20%) than
        budget/mood since name is mostly for categorization.
        """
        spot_name_lower = spot_name.lower()
        
        # TIER 1: PRIMARY DESTINATION TYPES - HIGH BOOST (0.9)
        tier1_keywords = ['beach', 'backwater', 'spiritual', 'devotion']
        for keyword in tier1_keywords:
            if keyword in spot_name_lower:
                return 0.9
        
        # TIER 2: SECONDARY DESTINATION TYPES (0.85)
        tier2_keywords = ['hill', 'mountain', 'snow', 'leh', 'ladakh', 'yoga']
        for keyword in tier2_keywords:
            if keyword in spot_name_lower:
                return 0.85
        
        # TIER 3: SPECIALTY KEYWORDS (0.75)
        tier3_keywords = ['night', 'life', 'city', 'tour']
        for keyword in tier3_keywords:
            if keyword in spot_name_lower:
                return 0.75
        
        # DEFAULT: Generic name (0.5)
        # Don't heavily penalize names without keywords
        return 0.5
    
    def _calculate_months_boost(self, spot_best_months: List[str], user_months: List[str]) -> float:
        """
        Score based on best months/season match.
        If user specifies preferred months or season, check if they match destination's best months.
        
        Supports: winter, summer, monsoon, autumn, and specific months
        """
        if not user_months or not spot_best_months:
            return 0.5  # Default if no months specified
        
        # Count matching months
        matches = sum(1 for month in user_months if month in spot_best_months)
        return min(1.0, matches / len(user_months))  # Max 1.0
    
    def _calculate_budget_score(self, budget_min: int, budget_max: int, user_budget_max: int, user_budget_min: Optional[int] = None) -> float:
        """
        Score based on budget fit.
        
        Args:
            budget_min: Spot's minimum budget
            budget_max: Spot's maximum budget
            user_budget_max: User's maximum budget
            user_budget_min: User's minimum budget (optional)
        """
        # Case 1: Range Query (e.g. 1000-2000)
        if user_budget_min is not None:
            # Check for overlap between [user_min, user_max] and [spot_min, spot_max]
            overlap_start = max(budget_min, user_budget_min)
            overlap_end = min(budget_max, user_budget_max)
            
            if overlap_start <= overlap_end:
                # There is an overlap!
                # Calculate how much of the spot's range is covered by user's range
                # or just return high score for overlap.
                return 1.0
            else:
                # No overlap, but we already filtered out strictly invalid ones.
                # This case shouldn't be reached if strict filtering is on, 
                # but just in case:
                return 0.5

        # Case 2: Max Limit Query (e.g. budget 2000)
        if budget_min <= user_budget_max <= budget_max:
            # User budget is within the spot's budget range
            # BONUS: Prioritize spots with LOWEST budget_min (most affordable)
            affordability_bonus = max(0, 1.0 - (budget_min / user_budget_max) * 0.1)
            return min(1.0, 1.0 + affordability_bonus)
        elif user_budget_max < budget_min:
            # User budget is too low - penalize significantly
            # (Should be filtered out by strict check, but keeping for robustness)
            return 0.0
        else:
            # User budget is higher than needed (user_budget_max > budget_max)
            # This is GOOD! The user can easily afford this.
            return 1.0
    
    def _calculate_mood_score(self, spot_moods: List[str], user_moods: List[str]) -> float:
        """
        Score based on mood match.
        Score = (matching moods) / (total user moods requested)
        """
        if not user_moods:
            return 1.0
        
        matches = sum(1 for mood in user_moods if mood in spot_moods)
        return matches / len(user_moods)
    
    def _calculate_duration_score(self, spot_duration: int, user_duration: int) -> float:
        """
        Score based on duration compatibility.
        
        CRITICAL: Heavily reward exact matches and penalize mismatches.
        When user specifies duration, it's a PRIMARY hard constraint.
        
        Scoring strategy:
        - Exact match (diff=0): 1.0 (perfect)
        - Off by 1 day: 0.90
        - Off by 2 days: 0.75  
        - Off by 3 days: 0.55
        - Beyond 3 days: very poor score (~0.30-0.40)
        
        This ensures exact matches always win over close mismatches.
        """
        diff = abs(spot_duration - user_duration)
        
        if diff == 0:
            return 1.0  # Exact match - highest score
        elif diff == 1:
            return 0.90  # Very close
        elif diff == 2:
            return 0.75  # Close but not ideal
        elif diff == 3:
            return 0.55  # Moderately different
        elif diff == 4:
            return 0.40  # Significantly different
        else:
            # Very large difference - heavy penalty
            return max(0.25, 1.0 - (diff * 0.12))
    
    def _calculate_distance_score(self, spot_distance: int, max_distance: int) -> float:
        """
        Score based on distance.
        Score = 1.0 if within max distance, else penalize
        Prefer closer spots within the limit
        """
        if spot_distance <= max_distance:
            # Prefer closer spots: bonus for being within distance
            proximity_score = 1.0 - (spot_distance / max_distance) * 0.3
            return min(1.0, proximity_score)
        else:
            # Beyond user's distance limit
            excess = spot_distance - max_distance
            penalty = min(excess / max_distance, 0.5)
            return max(0.3, 1.0 - penalty)
    
    def explain_score(self, spot_id: int, metadata: Dict, constraints: Dict) -> Dict:
        """
        Provide detailed breakdown of score components for a spot.
        
        Helps users understand why a destination was ranked in a certain position.
        """
        explanation = {
            'spot_id': spot_id,
            'spot_name': metadata['name'],
            'components': {}
        }
        
        # Budget (25% weight) - HIGHEST IMPACT
        if constraints.get('budget_max'):
            budget_score = self._calculate_budget_score(
                metadata['budget_min'],
                metadata['budget_max'],
                constraints['budget_max'],
                constraints.get('budget_min')
            )
            
            if constraints.get('budget_min'):
                reason = f"Budget ₹{metadata['budget_min']}-{metadata['budget_max']}, you want ₹{constraints['budget_min']}-{constraints['budget_max']}"
            else:
                reason = f"Budget ₹{metadata['budget_min']}-{metadata['budget_max']}, you have ₹{constraints['budget_max']}"
                
            explanation['components']['budget'] = {
                'score': round(budget_score * 0.25, 3),
                'reason': reason
            }
        else:
            explanation['components']['budget'] = {
                'score': round(0.5 * 0.25, 3),
                'reason': "No budget specified (default score)"
            }
        
        # Mood (25% weight)
        if constraints.get('mood'):
            mood_score = self._calculate_mood_score(metadata['mood'], constraints['mood'])
            explanation['components']['mood'] = {
                'score': round(mood_score * 0.25, 3),
                'reason': f"Moods: {metadata['mood']}, you want: {constraints['mood']}"
            }
        else:
            explanation['components']['mood'] = {
                'score': round(0.5 * 0.25, 3),
                'reason': "No mood specified (default score)"
            }
        
        # Destination Type (20% weight)
        name_boost = self._calculate_name_boost(metadata['name'], constraints)
        explanation['components']['destination_type'] = {
            'score': round(name_boost * 0.20, 3),
            'reason': f"Destination type: '{metadata['name']}' (boost: {name_boost})"
        }
        
        # Best Months (15% weight)
        if constraints.get('best_months'):
            months_boost = self._calculate_months_boost(
                metadata.get('best_months', []),
                constraints['best_months']
            )
            explanation['components']['best_months'] = {
                'score': round(months_boost * 0.15, 3),
                'reason': f"Best months: {metadata.get('best_months', [])}, you prefer: {constraints['best_months']}"
            }
        else:
            explanation['components']['best_months'] = {
                'score': round(0.5 * 0.15, 3),
                'reason': "No months specified (default score)"
            }
        
        # Duration (10% weight)
        if constraints.get('duration_days'):
            duration_score = self._calculate_duration_score(
                metadata['duration_days'],
                constraints['duration_days']
            )
            explanation['components']['duration'] = {
                'score': round(duration_score * 0.10, 3),
                'reason': f"Duration {metadata['duration_days']} days, you have {constraints['duration_days']} days"
            }
        else:
            explanation['components']['duration'] = {
                'score': round(0.5 * 0.10, 3),
                'reason': "No duration specified (default score)"
            }
        
        # Distance (5% weight)
        if constraints.get('distance_km'):
            distance_score = self._calculate_distance_score(
                metadata['distance_km'],
                constraints['distance_km']
            )
            explanation['components']['distance'] = {
                'score': round(distance_score * 0.05, 3),
                'reason': f"Distance {metadata['distance_km']}km, your limit {constraints['distance_km']}km"
            }
        else:
            explanation['components']['distance'] = {
                'score': round(0.5 * 0.05, 3),
                'reason': "No distance specified (default score)"
            }
        
        return explanation
