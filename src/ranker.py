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
        
        Weighted factors:
        - Budget (25%): Most important for user satisfaction
        - Name/Destination type (20%): Ensures right category of place
        - Mood (25%): User preference matching
        - Best months (15%): Travel planning
        - Duration (10%): Time availability
        - Distance (5%): Accessibility
        """
        score = 0.0
        
        # 1. BUDGET SCORE (25% weight) - HIGHEST PRIORITY
        # When user specifies budget, exact/close matches should rank highest
        if constraints.get('budget_max'):
            budget_score = self._calculate_budget_score(
                metadata['budget_min'],
                metadata['budget_max'],
                constraints['budget_max']
            )
            score += budget_score * 0.25
        else:
            score += 0.5 * 0.25
        
        # 2. MOOD SCORE (25% weight) - HIGH PRIORITY
        if constraints.get('mood'):
            mood_score = self._calculate_mood_score(metadata['mood'], constraints['mood'])
            score += mood_score * 0.25
        else:
            score += 0.5 * 0.25
        
        # 3. Place Name/Destination Type Boost (20% weight)
        # This ensures we're matching the right category of destination
        name_boost = self._calculate_name_boost(metadata['name'], constraints)
        score += name_boost * 0.20
        
        # 4. Best Months Match (15% weight)
        if constraints.get('best_months'):
            months_boost = self._calculate_months_boost(
                metadata.get('best_months', []),
                constraints['best_months']
            )
            score += months_boost * 0.15
        else:
            score += 0.5 * 0.15
        
        # 5. Duration Score (10% weight)
        if constraints.get('duration_days'):
            duration_score = self._calculate_duration_score(
                metadata['duration_days'],
                constraints['duration_days']
            )
            score += duration_score * 0.10
        else:
            score += 0.5 * 0.10
        
        # 6. Distance Score (5% weight) - LOWEST PRIORITY
        if constraints.get('distance_km'):
            distance_score = self._calculate_distance_score(
                metadata['distance_km'],
                constraints['distance_km']
            )
            score += distance_score * 0.05
        else:
            score += 0.5 * 0.05
        
        return score
    
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
        CRITICAL: Places where budget_min matches or is close to user's budget get highest score
        This ensures newly added affordable places rank first when searching by budget
        
        Scoring strategy:
        - Perfect match (budget = budget_min): 1.0 (user gets exact budget they need)
        - Very close (±₹500): 0.98-0.95
        - Within range: 0.90 (acceptable)
        - Slightly over budget: 0.85 (manageable)
        - Moderately over: 0.75
        - Way over: < 0.50
        """
        if budget_min <= user_budget <= budget_max:
            # User budget is within the spot's budget range
            # BOOST SCORE if budget_min is close to user's budget (newly added affordable places)
            budget_gap = abs(user_budget - budget_min)
            
            if budget_gap == 0:
                # PERFECT MATCH - user budget matches destination's minimum
                # This gives maximum priority to affordable options
                return 1.0
            elif budget_gap <= 500:
                # Very close to minimum budget - prioritize affordable options
                return 0.98
            elif budget_gap <= 1000:
                # Reasonably close
                return 0.95
            else:
                # Within range but not at minimum
                return 0.90
        elif user_budget < budget_min:
            # User budget is too low - penalize significantly
            deficit = budget_min - user_budget
            # CRITICAL: Less penalty if deficit is small (user can spend a bit more)
            if deficit <= 500:
                return 0.85  # Only slightly over budget
            elif deficit <= 1000:
                return 0.75  # Moderately over budget
            else:
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
                constraints['budget_max']
            )
            explanation['components']['budget'] = {
                'score': round(budget_score * 0.25, 3),
                'reason': f"Budget ₹{metadata['budget_min']}-{metadata['budget_max']}, you have ₹{constraints['budget_max']}"
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
