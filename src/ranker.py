"""
Ranker Module: Implements ranking and retrieval algorithms
Uses TF-IDF and constraint-based filtering for relevance ranking
"""
import math
from typing import Dict, List, Tuple
from src.indexer import TravelSpotIndexer


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
        
        Returns:
            List of (spot_id, score, metadata) tuples sorted by score
        """
        scores = {}
        
        for spot_id, metadata in self.indexer.spot_metadata.items():
            score = self._calculate_relevance_score(spot_id, metadata, constraints)
            scores[spot_id] = score
        
        # Sort by score (descending) and return top K
        ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        
        results = []
        for spot_id, score in ranked[:top_k]:
            metadata = self.indexer.get_spot_by_id(spot_id)
            results.append((spot_id, score, metadata))
        
        return results
    
    def _calculate_relevance_score(self, spot_id: int, metadata: Dict, constraints: Dict) -> float:
        """
        Calculate relevance score for a spot.
        Factors: place_name (highest), name_boost, mood, best_months, budget, duration, distance
        """
        score = 0.0
        
        # CRITICAL: Place Name Match (50% weight if exact place name specified)
        # This is the HIGHEST priority - direct destination match
        place_name_boost = 0.0
        if constraints.get('place_name'):
            # Check if this is the exact destination being searched for
            if constraints['place_name'].lower() == metadata['name'].lower():
                # Perfect match!
                place_name_boost = 1.0
                score += place_name_boost * 0.50  # 50% weight for place name match
            else:
                # Not the exact place being searched for, but might match a keyword
                # Use keyword matching with reduced weight
                name_boost = self._calculate_name_boost(metadata['name'], constraints)
                score += name_boost * 0.25  # Only 25% for keyword match when place name specified
        else:
            # No explicit place name search, use keyword matching
            # 0. Destination Name Keyword Boost (40% weight)
            name_boost = self._calculate_name_boost(metadata['name'], constraints)
            score += name_boost * 0.40
        
        # 1. Best Months Match (15% weight)
        if constraints.get('best_months'):
            months_boost = self._calculate_months_boost(
                metadata.get('best_months', []),
                constraints['best_months']
            )
            score += months_boost * 0.15
        else:
            score += 0.5 * 0.15
        
        # 2. Mood Score (20% weight)
        if constraints.get('mood'):
            mood_score = self._calculate_mood_score(metadata['mood'], constraints['mood'])
            score += mood_score * 0.20
        else:
            score += 0.5 * 0.20
        
        # 3. Budget Score (10% weight)
        if constraints.get('budget_max'):
            budget_score = self._calculate_budget_score(
                metadata['budget_min'],
                metadata['budget_max'],
                constraints['budget_max']
            )
            score += budget_score * 0.10
        else:
            score += 0.5 * 0.10
        
        # 4. Duration Score (3% weight)
        if constraints.get('duration_days'):
            duration_score = self._calculate_duration_score(
                metadata['duration_days'],
                constraints['duration_days']
            )
            score += duration_score * 0.03
        else:
            score += 0.5 * 0.03
        
        # 5. Distance Score (2% weight)
        if constraints.get('distance_km'):
            distance_score = self._calculate_distance_score(
                metadata['distance_km'],
                constraints['distance_km']
            )
            score += distance_score * 0.02
        else:
            score += 0.5 * 0.02
        
        return score
    
    def _calculate_name_boost(self, spot_name: str, constraints: Dict) -> float:
        """
        CRITICAL: Boost score if spot name directly matches mood constraints.
        This is the MOST IMPORTANT factor - ensures "hill" shows ONLY hills!
        """
        spot_name_lower = spot_name.lower()
        
        # TIER 1: EXACT KEYWORDS - ABSOLUTE MAXIMUM (1.0)
        # These are 100% relevant to the query
        tier1_keywords = ['hill', 'mountain', 'snow', 'leh', 'ladakh']
        for keyword in tier1_keywords:
            if keyword in spot_name_lower:
                return 1.0  # ABSOLUTE MAXIMUM SCORE
        
        # TIER 2: STRONG SECONDARY KEYWORDS (0.75)
        tier2_keywords = ['backwater', 'beach', 'yoga']
        for keyword in tier2_keywords:
            if keyword in spot_name_lower:
                return 0.75
        
        # TIER 3: WEAK KEYWORDS (0.5)
        tier3_keywords = ['city', 'tour', 'spiritual', 'night', 'life']
        for keyword in tier3_keywords:
            if keyword in spot_name_lower:
                return 0.5
        
        # DEFAULT: No name match at all (0.1)
        # This heavily penalizes non-matching destinations
        return 0.1
    
    def _calculate_months_boost(self, spot_best_months: List[str], user_months: List[str]) -> float:
        """
        Score based on best months match.
        If user specifies preferred months, check if they match destination's best months
        """
        if not user_months or not spot_best_months:
            return 0.5  # Default if no months specified
        
        # Count matching months
        matches = sum(1 for month in user_months if month in spot_best_months)
        return min(1.0, matches / len(user_months))  # Max 1.0
    
    def _calculate_budget_score(self, budget_min: int, budget_max: int, user_budget: int) -> float:
        """
        Score based on budget fit.
        Score = 1.0 if user budget is within spot range, else penalize
        """
        if budget_min <= user_budget <= budget_max:
            return 1.0  # Perfect fit - 100 points
        elif user_budget < budget_min:
            # User budget is too low - penalize significantly
            deficit = budget_min - user_budget
            penalty = min(deficit / budget_min, 0.7)  # Max 70% penalty
            return max(0.3, 1.0 - penalty)
        else:
            # User budget is higher than needed
            # More expensive spots get lower score when user wants cheap
            overage = user_budget - budget_max
            if overage > budget_max:  # Much more expensive than budget
                return 0.5
            else:
                return 0.85  # Acceptable for overspending
    
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
        Prefer spots with duration close to user's available time
        """
        diff = abs(spot_duration - user_duration)
        
        if diff == 0:
            return 1.0  # Perfect match
        elif diff <= 1:
            return 0.9  # Very close
        elif diff <= 2:
            return 0.7  # Close
        else:
            return max(0.4, 1.0 - (diff * 0.1))  # Penalize larger differences
    
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
        Provide breakdown of score components for explanation
        """
        explanation = {
            'spot_id': spot_id,
            'spot_name': metadata['name'],
            'components': {}
        }
        
        # CRITICAL: Add name_boost (40% weight) - this is the DOMINANT factor
        name_boost = self._calculate_name_boost(metadata['name'], constraints)
        explanation['components']['name_boost'] = {
            'score': round(name_boost * 0.40, 3),
            'reason': f"Destination name '{metadata['name']}' matching keywords (boost multiplier: {name_boost})"
        }
        
        # Mood (35% weight)
        if constraints.get('mood'):
            mood_score = self._calculate_mood_score(metadata['mood'], constraints['mood'])
            explanation['components']['mood'] = {
                'score': round(mood_score * 0.35, 3),
                'reason': f"Spot moods: {metadata['mood']}, requested: {constraints['mood']}"
            }
        else:
            explanation['components']['mood'] = {
                'score': round(0.5 * 0.35, 3),
                'reason': f"No mood specified (default score)"
            }
        
        # Budget (15% weight)
        if constraints.get('budget_max'):
            budget_score = self._calculate_budget_score(
                metadata['budget_min'],
                metadata['budget_max'],
                constraints['budget_max']
            )
            explanation['components']['budget'] = {
                'score': round(budget_score * 0.15, 3),
                'reason': f"Budget ₹{metadata['budget_min']}-{metadata['budget_max']}, user has ₹{constraints['budget_max']}"
            }
        else:
            explanation['components']['budget'] = {
                'score': round(0.5 * 0.15, 3),
                'reason': f"No budget specified (default score)"
            }
        
        # Duration (7% weight)
        if constraints.get('duration_days'):
            duration_score = self._calculate_duration_score(
                metadata['duration_days'],
                constraints['duration_days']
            )
            explanation['components']['duration'] = {
                'score': round(duration_score * 0.07, 3),
                'reason': f"Duration {metadata['duration_days']} days, user has {constraints['duration_days']} days"
            }
        else:
            explanation['components']['duration'] = {
                'score': round(0.5 * 0.07, 3),
                'reason': f"No duration specified (default score)"
            }
        
        # Distance (3% weight)
        if constraints.get('distance_km'):
            distance_score = self._calculate_distance_score(
                metadata['distance_km'],
                constraints['distance_km']
            )
            explanation['components']['distance'] = {
                'score': round(distance_score * 0.03, 3),
                'reason': f"Distance {metadata['distance_km']}km, user limit {constraints['distance_km']}km"
            }
        else:
            explanation['components']['distance'] = {
                'score': round(0.5 * 0.03, 3),
                'reason': f"No distance specified (default score)"
            }
        
        return explanation
