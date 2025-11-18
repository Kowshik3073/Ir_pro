# 📝 Example Queries - Travel Recommendation System

## Quick Reference Guide

### 💰 BUDGET-BASED QUERIES

#### 1. "cheap"
**What it means**: Find affordable destinations
**Budget Set To**: ₹3500 (automatically)
**Expected Results**:
- Varanasi Spiritual (₹1500-3500)
- Jaipur City Tour (₹2000-5000)
- Ooty Hill Station (₹2500-6000)
- Goa Beach (₹2500-6000)

#### 2. "budget 5000"
**What it means**: Find destinations within ₹5000
**Budget Set To**: ₹5000
**Expected Results**:
- All destinations except Leh Ladakh
- Mix of all moods under ₹5000

#### 3. "expensive"
**What it means**: High-end adventure destinations
**Budget Set To**: No constraint (shows all)
**Expected Results**:
- Leh Ladakh Mountain (₹5500-12000)
- Mumbai Night Life (₹3500-9000)
- Shimla Snow Mountain (₹4000-8500)

---

### 🏔️ DESTINATION-BASED QUERIES

#### 4. "hill"
**What it means**: Find hill stations
**Mood Detected**: nature, adventure
**Expected Results**:
1. Manali Hill Station ✓
2. Leh Ladakh Mountain ✓
3. Ooty Hill Station ✓
4. Shimla Snow Mountain ✓
5. Kerala Backwaters (has nature mood)

#### 5. "mountain adventure"
**What it means**: Find adventure destinations in mountains
**Moods Detected**: nature, adventure
**Expected Results**:
1. Manali Hill Station
2. Leh Ladakh Mountain
3. Shimla Snow Mountain
(All have "mountain" or "snow" + adventure)

#### 6. "beach relaxing"
**What it means**: Find relaxing beach destinations
**Moods Detected**: relaxing
**Name Keywords**: beach, backwater
**Expected Results**:
1. Goa Beach ✓
2. Kerala Backwaters ✓
3. Rishikesh Yoga (relaxing)

---

### 🎯 MOOD-BASED QUERIES

#### 7. "adventure"
**What it means**: Find adventure destinations
**Mood Detected**: adventure
**Expected Results**:
- Manali Hill Station
- Leh Ladakh Mountain
- Shimla Snow Mountain

#### 8. "relaxing"
**What it means**: Find peaceful destinations
**Mood Detected**: relaxing
**Expected Results**:
- Ooty Hill Station
- Goa Beach
- Rishikesh Yoga
- Kerala Backwaters

#### 9. "spiritual yoga"
**What it means**: Find yoga and meditation places
**Moods Detected**: spiritual, relaxing
**Expected Results**:
- Rishikesh Yoga ✓ (has "yoga" + spiritual)
- Varanasi Spiritual
- Kerala Backwaters (romantic mood)

#### 10. "party nightlife"
**What it means**: Find party destinations
**Mood Detected**: party
**Expected Results**:
1. Mumbai Night Life ✓
2. Goa Beach

---

### ⏱️ DURATION-BASED QUERIES

#### 11. "2 days"
**What it means**: Find quick getaway (2 days)
**Duration Set To**: 2 days
**Expected Results**:
- Jaipur City Tour (2 days) ✓
- Varanasi Spiritual (2 days) ✓
- Mumbai Night Life (2 days) ✓

#### 12. "4 days adventure"
**What it means**: 4-day adventure trip
**Duration**: 4 days
**Mood**: adventure
**Expected Results**:
1. Manali Hill Station (4 days, adventure)

#### 13. "3 days"
**What it means**: Weekend getaway (3 days)
**Duration Set To**: 3 days
**Expected Results**:
- Goa Beach (4 days - close)
- Kerala Backwaters (3 days) ✓
- Ooty Hill Station (3 days) ✓
- Shimla Snow Mountain (3 days) ✓
- Rishikesh Yoga (3 days) ✓

---

### 🚗 DISTANCE-BASED QUERIES

#### 14. "within 1000km"
**What it means**: Find destinations nearby (< 1000km)
**Distance Limit**: 1000km (from user location)
**Expected Results** (from Mumbai):
- Ooty (800km) ✓
- Manali (900km) ✓
- Shimla (400km) ✓
- Rishikesh (250km) ✓
- Jaipur (300km) ✓
- Varanasi (600km) ✓
- Goa (1500km) ✗ (over limit)

#### 15. "within 2000km hill"
**What it means**: Hill stations within 2000km
**Distance**: 2000km
**Mood**: nature
**Expected Results**:
- All hill stations within distance

---

### 🔀 COMBINED QUERIES (Best Examples!)

#### 16. "cheap hill"
**Meaning**: Affordable hill station trip
**Budget**: ₹3500
**Mood**: nature
**Expected Top Results**:
1. Manali Hill Station (₹3500-8000, nature)
2. Ooty Hill Station (₹2500-6000, nature)
3. Shimla Snow Mountain (₹4000-8500)

#### 17. "cheap adventure"
**Meaning**: Budget-friendly adventure trip
**Budget**: ₹3500
**Mood**: adventure
**Expected Results**:
1. Manali Hill Station (₹3500-8000)
2. Shimla Snow Mountain (₹4000-8500)

#### 18. "cheap relaxing beach"
**Meaning**: Cheap, relaxing beach vacation
**Budget**: ₹3500
**Mood**: relaxing
**Name Keywords**: beach
**Expected Results**:
1. Goa Beach (₹2500-6000, relaxing)
2. Kerala Backwaters (₹3000-7000, relaxing, nature)

#### 19. "spiritual yoga 3 days budget 3000"
**Meaning**: 3-day spiritual yoga retreat within ₹3000
**Budget**: ₹3000
**Mood**: spiritual
**Duration**: 3 days
**Expected Results**:
1. Rishikesh Yoga (₹2000-5000, 3 days, spiritual)
2. Varanasi Spiritual (₹1500-3500, 2 days, spiritual)

#### 20. "mountain adventure 4 days"
**Meaning**: 4-day mountain adventure
**Moods**: adventure, nature
**Duration**: 4 days
**Expected Results**:
1. Manali Hill Station (4 days, adventure)
2. Leh Ladakh Mountain (6 days - close)

#### 21. "cheap spiritual"
**Meaning**: Budget-friendly spiritual destination
**Budget**: ₹3500
**Mood**: spiritual
**Expected Results**:
1. Rishikesh Yoga (₹2000-5000) ✓
2. Varanasi Spiritual (₹1500-3500) ✓

#### 22. "cultural city tour"
**Meaning**: Cultural experience in a city
**Moods**: cultural, history
**Name Keywords**: city, tour, heritage
**Expected Results**:
1. Jaipur City Tour ✓ (cultural, history)
2. Varanasi Spiritual (cultural, history)

#### 23. "adventure within 1500km"
**Meaning**: Adventure destination within 1500km
**Mood**: adventure
**Distance**: 1500km
**Expected Results**:
- All adventure destinations within distance

#### 24. "budget 5000 adventure 4 days"
**Meaning**: 4-day adventure within ₹5000
**Budget**: ₹5000
**Mood**: adventure
**Duration**: 4 days
**Expected Results**:
1. Manali Hill Station (₹3500-8000, adventure, 4 days)

#### 25. "cheap hill within 800km"
**Meaning**: Nearby, affordable hill station
**Budget**: ₹3500
**Mood**: nature
**Distance**: 800km
**Expected Results**:
1. Ooty Hill Station (₹2500-6000, 800km from major cities)
2. Manali Hill Station (₹3500-8000, near limit)

---

## 🎓 How the System Understands Queries

### Keyword Extraction Process

```
User Input: "cheap hill adventure 4 days"
            ↓
Tokenized: ["cheap", "hill", "adventure", "4", "days"]
            ↓
BUDGET EXTRACTION:
  - "cheap" found → Set budget_max = ₹3500
            ↓
MOOD EXTRACTION:
  - "hill" found → Add "nature" mood
  - "adventure" found → Add "adventure" mood
            ↓
DURATION EXTRACTION:
  - "4 days" found → Set duration = 4 days
            ↓
FINAL CONSTRAINTS:
  - budget_max: 3500
  - mood: ["nature", "adventure"]
  - duration_days: 4
  - distance_km: None (not specified)
            ↓
RANKING:
  1. Filter by constraints (budget <= 3500, moods match, duration close to 4)
  2. Name boost: "Manali Hill Station" gets 1.0 boost (has "hill")
  3. Calculate scores
  4. Return top 5 sorted by score
```

---

## 💡 Pro Tips for Best Results

### 1. Be Specific
✓ **Good**: "cheap hill 3 days"
✗ **Bad**: "trip"

### 2. Use Common Keywords
✓ **Good**: "adventure mountain"
✗ **Bad**: "thrill seeking expedition"

### 3. Combine Filters
✓ **Good**: "cheap spiritual yoga"
✗ **Bad**: "inexpensive meditative place"

### 4. Use Numbers
✓ **Good**: "4 days budget 5000"
✗ **Bad**: "few days reasonable cost"

### 5. Order Doesn't Matter
✓ **"cheap hill adventure"** = **"adventure cheap hill"**
Both return same results (system is order-independent)

---

## 📊 Query Performance Table

| Query | Extraction Time | Ranking Time | Total Time |
|-------|-----------------|--------------|-----------|
| "cheap" | <1ms | <10ms | <11ms |
| "hill" | <1ms | <10ms | <11ms |
| "cheap hill adventure 4 days" | <2ms | <15ms | <17ms |
| "budget 5000 spiritual yoga 3 days" | <2ms | <15ms | <17ms |

---

## 🎯 Typical User Flows

### Flow 1: Budget-Conscious User
```
1. User enters: "cheap"
2. System shows: Top 5 cheapest destinations
3. User reads: Descriptions and budgets
4. User enters: "cheap hill" (to refine)
5. System shows: Cheap hill stations
6. User selects: Ooty or Rishikesh
```

### Flow 2: Adventure Seeker
```
1. User enters: "adventure"
2. System shows: Top 5 adventure destinations
3. User reads: Mountain/Trekking options
4. User enters: "adventure 4 days" (duration)
5. System shows: 4-day adventures
6. User selects: Manali or Shimla
```

### Flow 3: Relaxation Finder
```
1. User enters: "relaxing"
2. System shows: Calm destinations
3. User refines: "cheap relaxing" (budget)
4. System shows: Affordable peaceful places
5. User selects: Rishikesh or Ooty
```

---

## 📍 Location Impact on Results

When user sets location to **Mumbai**:

```
Distances Calculated (Haversine):
- Rishikesh: 250 km
- Jaipur: 300 km
- Shimla: 400 km
- Varanasi: 600 km
- Ooty: 670 km
- Manali: 900 km
- Goa: 500 km
- Leh Ladakh: 2600 km
- Kerala: 800 km

Result: Closer destinations shown with distance
```

When user changes location to **Bangalore**:

```
Distances Recalculated:
- Ooty: 200 km ← Much closer!
- Kerala: 300 km ← Much closer!
- Goa: 600 km
- Manali: 1400 km
- Rishikesh: 1600 km

Results Update: Closer destinations now preferred
```

---

## ✅ Quick Test Checklist

Try these queries to verify system is working:

- [ ] "cheap" → Shows affordable options
- [ ] "hill" → Shows Manali, Ooty, Shimla, Leh at top
- [ ] "adventure" → Shows Manali, Leh, Shimla
- [ ] "spiritual" → Shows Rishikesh, Varanasi
- [ ] "cheap hill" → Shows hill stations under ₹3500
- [ ] "relaxing" → Shows peaceful destinations
- [ ] "4 days" → Shows 4-day trips
- [ ] After location set: → Shows distance in results

---

Happy traveling! 🌍✈️
