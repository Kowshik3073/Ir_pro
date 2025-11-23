
import sys
import os
from pathlib import Path
import json

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.recommendation_system import TravelSpotRecommendationSystem

def calculate_metrics():
    # 1. Initialize System
    dataset_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'travel_spots.json')
    system = TravelSpotRecommendationSystem(dataset_path)
    
    # 2. Define Test Set (Query, Expected Constraints/Keywords for Relevance)
    # We define relevance logically:
    # - If query has budget, relevant docs MUST be within budget.
    # - If query has mood, relevant docs MUST have that mood.
    # - If query has keyword, relevant docs MUST contain keyword in name/desc/mood.
    
    test_queries = [
        {"query": "beaches", "type": "keyword", "term": "beach"},
        {"query": "mountains", "type": "keyword", "term": "mountain"}, # Handles 'hill' via synonym
        {"query": "adventure", "type": "mood", "term": "adventure"},
        {"query": "relaxing", "type": "mood", "term": "relaxing"},
        {"query": "budget 5000", "type": "budget", "max": 5000},
        {"query": "under 10000", "type": "budget", "max": 10000},
        {"query": "nature trip", "type": "mood", "term": "nature"},
        {"query": "spiritual places", "type": "mood", "term": "spiritual"},
        {"query": "goa", "type": "name", "term": "goa"},
        {"query": "kerala backwaters", "type": "name", "term": "kerala"},
        {"query": "adventure budget 4000", "type": "mixed", "mood": "adventure", "budget": 4000},
        {"query": "romantic honeymoon", "type": "mood", "term": "romantic"},
        {"query": "history and culture", "type": "mood", "term": "history"}, # 'culture' handled by mapping?
        {"query": "snow", "type": "keyword", "term": "snow"},
        {"query": "temples", "type": "keyword", "term": "temple"}
    ]
    
    total_precision = 0
    total_recall = 0
    total_f1 = 0
    
    print(f"{'Query':<30} | {'P@5':<6} | {'R@5':<6} | {'F1':<6}")
    print("-" * 60)
    
    for test in test_queries:
        query = test['query']
        results = system.recommend_with_explanation(query, top_k=5)
        # Slice to Top 5 for P@5 and R@5 metrics
        retrieved_docs = results['recommendations'][:5]
        
        # Determine Ground Truth (Relevant Docs in entire dataset)
        relevant_docs_count = 0
        relevant_ids = set()
        
        for spot_id, spot in system.data_indexer.destination_info.items():
            is_relevant = False
            
            if test['type'] == 'keyword':
                # Check if term in name, mood, or description
                term = test['term']
                text = (spot['name'] + ' ' + spot['description'] + ' ' + ' '.join(spot['mood'])).lower()
                # Simple check: if term is in text OR if synonym logic applies (e.g. mountain/hill)
                if term in text:
                    is_relevant = True
                elif term == 'mountain' and 'hill' in text:
                    is_relevant = True
                elif term == 'hill' and 'mountain' in text:
                    is_relevant = True
                    
            elif test['type'] == 'mood':
                if test['term'] in [m.lower() for m in spot['mood']]:
                    is_relevant = True
                    
            elif test['type'] == 'budget':
                if spot['budget_min'] <= test['max']:
                    is_relevant = True
            
            elif test['type'] == 'name':
                if test['term'] in spot['name'].lower():
                    is_relevant = True
                    
            elif test['type'] == 'mixed':
                # Must match BOTH
                mood_match = test['mood'] in [m.lower() for m in spot['mood']]
                budget_match = spot['budget_min'] <= test['budget']
                if mood_match and budget_match:
                    is_relevant = True
            
            if is_relevant:
                relevant_docs_count += 1
                relevant_ids.add(spot_id)
        
        # Calculate P@5 and R@5 for this query
        retrieved_relevant = 0
        for rec in retrieved_docs:
            if rec['spot_id'] in relevant_ids:
                retrieved_relevant += 1
        
        # Precision: Relevant Retrieved / Total Retrieved (Top 5)
        # If less than 5 retrieved, use actual count
        k = len(retrieved_docs)
        precision = retrieved_relevant / k if k > 0 else 0
        
        # Recall: Relevant Retrieved / Total Relevant in Dataset
        # Note: Recall@5 is capped by k. If there are 10 relevant docs, max recall is 0.5.
        # Standard Recall@k definition: relevant_in_top_k / total_relevant
        recall = retrieved_relevant / relevant_docs_count if relevant_docs_count > 0 else 0
        
        # F1 Score
        if precision + recall > 0:
            f1 = 2 * (precision * recall) / (precision + recall)
        else:
            f1 = 0
            
        total_precision += precision
        total_recall += recall
        total_f1 += f1
        
        print(f"{query:<30} | {precision:.2f}   | {recall:.2f}   | {f1:.2f}")
        
    # Averages
    avg_precision = total_precision / len(test_queries)
    avg_recall = total_recall / len(test_queries)
    avg_f1 = total_f1 / len(test_queries)
    
    print("-" * 60)
    print(f"{'AVERAGE':<30} | {avg_precision:.2f}   | {avg_recall:.2f}   | {avg_f1:.2f}")
    
    # Update the markdown file with REAL values
    update_markdown(avg_precision, avg_recall, avg_f1)

def update_markdown(p, r, f1):
    filepath = os.path.join(os.path.dirname(__file__), '..', 'experimentation_results.md')
    
    # Read existing file
    with open(filepath, 'r') as f:
        content = f.read()
    
    # We will just append the Real Results section or replace the table values if I could parse it easily.
    # For simplicity, I'll append a "Verified Real-World Performance" section.
    
    new_section = f"""
## F. Verified Real-World Performance (Live Test)
We ran a live evaluation script (`tests/calculate_metrics.py`) on the current codebase using 15 standard queries.
The **actual** performance metrics for the Hybrid Weighted Scoring System are:

| Metric | Score |
| :--- | :---: |
| **Precision@5** | **{p:.2f}** |
| **Recall@5** | **{r:.2f}** |
| **F1 Score** | **{f1:.2f}** |

*Note: These values are calculated dynamically based on the current dataset and ranking logic.*
"""
    
    # Check if section already exists to avoid duplication
    if "## F. Verified Real-World Performance" not in content:
        with open(filepath, 'a') as f:
            f.write(new_section)
        print("\nUpdated experimentation_results.md with real metrics.")
    else:
        print("\nMetrics section already exists. Please update manually if needed.")

if __name__ == "__main__":
    calculate_metrics()
