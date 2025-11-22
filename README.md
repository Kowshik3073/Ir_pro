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

### 1. Vector Space Model & TF-IDF
*   **TF-IDF (Term Frequency-Inverse Document Frequency)** is used to analyze the textual descriptions of travel spots.
*   It helps the system understand which words are important for each destination, allowing it to match your query keywords against the rich descriptions of places.

### 2. Weighted Scoring System
Instead of a simple "yes/no" match, we use a sophisticated scoring algorithm to rank results. The final score is a weighted sum of several factors:
*   **Budget Match (25%)**: Heavily weighted to ensure affordability.
*   **Mood/Category Match (20%)**: Ensures the "vibe" is right.
*   **Duration Match (20%)**: Prioritized if you specify a trip length.
*   **Content Relevance (15%)**: How well the description matches your keywords.
*   **Name Match (12%)**: Direct matches (e.g., searching "Goa") get a boost.
*   **Best Time to Visit (5%)**: Slight boost if it's the right season.

### 3. Boolean Retrieval & Filtering
*   We use **Strict Filtering** logic for critical constraints. If you set a maximum budget, places significantly more expensive are strictly excluded (Boolean NOT).
*   If you search for a specific type (e.g., "Beach"), the system enforces a filter to exclude non-matching categories.

### 4. Natural Language Processing (NLP)
*   **Entity Recognition**: Extracting money amounts (`MONEY` entities) and dates (`DATE` entities) from text.
*   **Noun Chunking**: Understanding phrases like "relaxing trip" to identify user intent.

## 💻 Tech Stack
*   **Backend**: Python, Flask
*   **Frontend**: HTML5, CSS3 (Modern Dark Theme), JavaScript (Vanilla)
*   **IR/NLP Libraries**: `scikit-learn` (TF-IDF), `spaCy` (NLP)
*   **Data**: JSON-based document store

---
*Built with ❤️ for the Information Retrieval Project*
