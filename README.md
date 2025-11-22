# 🌍 Travel Finder - Smart Travel Recommendation System

## 📖 What is this?
**Travel Finder** is an intelligent web application designed to help users discover their perfect travel destinations in India. Unlike traditional travel sites that rely on rigid filters, Travel Finder understands **natural language queries**.

You can ask it things like:
*   *"I want a beach vacation under 5000 rupees"*
*   *"Adventure trip in the mountains for 3 days"*
*   *"Romantic getaway in Kerala"*

The system analyzes your request, understands your intent (budget, mood, duration), and ranks the best travel spots using advanced Information Retrieval (IR) techniques.

## 🚀 Why should anyone use it?
Finding the right travel spot can be overwhelming. Travel Finder solves this by:
1.  **Understanding You**: It parses natural language, so you don't have to click through dozens of checkboxes.
2.  **Smart Budgeting**: It understands budget ranges (e.g., "3000-5000") and finds places that fit your wallet, even if their prices overlap slightly.
3.  **Relevance Ranking**: It doesn't just show random places; it ranks them based on how well they match *your* specific criteria (mood, price, duration, etc.).
4.  **Distance Calculation**: It automatically calculates the distance from your city to every destination, helping you plan travel logistics.
5.  **Visual & Fast**: A beautiful, dark-themed UI that provides instant results with no clutter.

## 🛠️ How it works?
The system follows a sophisticated pipeline to deliver recommendations:

1.  **User Input**: You type a query (e.g., "budget 5000 beach").
2.  **Query Processing (NLP)**:
    *   The backend uses **spaCy** (Natural Language Processing) to break down your sentence.
    *   It extracts **Constraints**:
        *   **Budget**: "5000" (max) or "2000-5000" (range).
        *   **Mood**: "beach" -> maps to internal tags like "relaxing", "party".
        *   **Duration**: "3 days".
3.  **Information Retrieval & Ranking**:
    *   The system searches its database of 35+ curated Indian destinations.
    *   It applies **Strict Filtering** (e.g., if you say "beach", it won't show mountains).
    *   It calculates a **Relevance Score** for each spot based on weighted factors.
4.  **Response**: The top-ranked results are sent to the frontend.
5.  **Frontend Display**:
    *   The browser calculates the **Distance** using the Haversine formula based on your location.
    *   Results are displayed with rich details: rating, best time to visit, and cost.

## 🧠 Information Retrieval (IR) Concepts Used
This project implements core concepts from Information Retrieval and Search Engine design:

### 1. Inverted Index
*   **Fast Keyword Lookup**: We build an inverted index mapping terms to destination IDs for efficient retrieval.
*   **Document Frequency Tracking**: Track how many destinations contain each term for relevance calculations.
*   **Tokenization**: Text is processed into searchable terms with stop word removal and length filtering.

### 2. Weighted Scoring System
Instead of a simple "yes/no" match, we use a sophisticated multi-factor scoring algorithm to rank results. The final relevance score is a weighted sum of several factors:
*   **Budget Match (25%)**: Heavily weighted to ensure affordability and budget overlap detection.
*   **Mood/Category Match (20%)**: Ensures the "vibe" matches user preferences.
*   **Duration Match (20%)**: Prioritized when trip length is explicitly specified.
*   **Content Relevance (15%)**: Keyword matching in destination names and descriptions.
*   **Destination Type (12%)**: Boosts for matching destination categories (beach, mountain, etc.).
*   **Best Time to Visit (5%)**: Seasonal matching for optimal travel timing.
*   **Distance (3%)**: Proximity to user's location.

### 3. Boolean Retrieval & Filtering
*   **Strict Budget Filtering**: Places outside budget range are excluded using Boolean logic.
*   **Category Filtering**: Enforces type matching (e.g., "beach" queries exclude non-beach destinations).
*   **Overlap Detection**: Smart budget range matching allows partial overlaps.

### 4. Natural Language Query Processing
*   **Budget Extraction**: Parses budget ranges ("1000-2000") and single values ("under 5000").
*   **Mood Detection**: Maps keywords to mood categories (adventure, relaxing, cultural, etc.).
*   **Duration Parsing**: Extracts trip length from queries ("3 days", "for 5 days").
*   **Location Recognition**: Identifies destination names and aliases.
*   **Stop Word Removal**: Filters common words to extract meaningful search terms.

### 5. Relevance Ranking
*   **Adaptive Weighting**: Scoring weights adjust based on explicit user constraints.
*   **Threshold-Based Filtering**: Only results above 40% relevance are shown.
*   **Multi-Criteria Scoring**: Combines multiple signals for comprehensive relevance assessment.

## 💻 Tech Stack
*   **Backend**: Python 3.x with HTTP Server
*   **Frontend**: HTML5, CSS3 (Modern Dark Theme), Vanilla JavaScript
*   **Data Storage**: JSON-based document store
*   **Algorithms**: Custom weighted scoring, inverted indexing, constraint satisfaction

---
*Built with ❤️ for the Information Retrieval Project*
