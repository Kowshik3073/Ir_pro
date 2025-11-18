# Travel Spot Recommendation System

## Quick Start

### 1. Start the Backend Server
```bash
cd /Users/tanujkinjarapu/Desktop/Ir_pro
python3 server.py
```

The server will run on `http://localhost:8000`

### 2. Open the Web Interface
Open your browser and go to:
```
http://localhost:8000/index.html
```

### 3. Use the System
- Type a query in the textarea, e.g., "Budget 5000, adventure for 4 days within 1000km"
- Click "Find Destinations"
- View ranked recommendations with scores and breakdowns

### Quick Example Queries
- "Budget 2000"
- "Adventure mood"
- "Relaxing vacation"
- "Budget 5000, adventure for 4 days"
- "Spiritual and cultural"

## API Endpoints

### POST /api/recommend
Get travel recommendations

```bash
curl -X POST http://localhost:8000/api/recommend \
  -H "Content-Type: application/json" \
  -d '{"query": "Budget 5000, adventure", "top_k": 5}'
```

### GET /api/all-spots
Get all available destinations

```bash
curl http://localhost:8000/api/all-spots
```

### GET /api/health
Health check

```bash
curl http://localhost:8000/api/health
```

## Project Structure

```
Ir_pro/
├── src/                    # Python IR System
│   ├── indexer.py
│   ├── query_processor.py
│   ├── ranker.py
│   └── recommendation_system.py
│
├── data/
│   └── travel_spots.json   # Dataset (10 destinations)
│
├── tests/
│   └── test_recommendation_system.py  # 19 unit tests
│
├── web/                    # Web Frontend
│   ├── index.html         # Main page
│   ├── styles.css         # Styling
│   └── app.js             # Frontend logic
│
└── server.py              # Backend API server
```

## Testing

Run unit tests:
```bash
python3 -m unittest tests.test_recommendation_system -v
```

Result: ✅ 19/19 tests PASSED

## Features

✨ Natural language query support  
✨ Multi-factor intelligent ranking  
✨ Explainable results with score breakdowns  
✨ Beautiful web interface  
✨ Fast API (milliseconds per query)  
✨ 10 travel destinations pre-indexed  
✨ Responsive design (works on mobile too)
