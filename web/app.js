// Travel Spot Recommendation System - Frontend
// Connects to Python backend for recommendations

class TravelRecommendationApp {
    constructor() {
        this.baseURL = 'http://localhost:8001'; // Python server URL
        this.userLocation = localStorage.getItem('userLocation') || null;
        this.currentResults = []; // Store current results for sorting
        this.locationCoordinates = {
            // Major Indian cities for distance calculation
            'mumbai': { lat: 19.0760, lng: 72.8777 },
            'delhi': { lat: 28.7041, lng: 77.1025 },
            'bangalore': { lat: 12.9716, lng: 77.5946 },
            'hyderabad': { lat: 17.3850, lng: 78.4867 },
            'jaipur': { lat: 26.9124, lng: 75.7873 },
            'kolkata': { lat: 22.5726, lng: 88.3639 },
            'pune': { lat: 18.5204, lng: 73.8567 },
            'ahmedabad': { lat: 23.0225, lng: 72.5714 },
            'chennai': { lat: 13.0827, lng: 80.2707 },
            'goa': { lat: 15.4909, lng: 73.8278 },
            'manali': { lat: 32.2392, lng: 77.1892 },
            'shimla': { lat: 31.1048, lng: 77.1734 },
            'ooty': { lat: 11.4102, lng: 76.6955 },
            'kerala': { lat: 10.8505, lng: 76.2711 },
            'kochi': { lat: 9.9312, lng: 76.2673 },
            'leh': { lat: 34.1526, lng: 77.5770 },
            'varanasi': { lat: 25.3200, lng: 82.9850 },
            'rishikesh': { lat: 30.0889, lng: 78.2676 },
            'udaipur': { lat: 24.5854, lng: 73.7125 },
            'agra': { lat: 27.1767, lng: 78.0081 },
            'amritsar': { lat: 31.6340, lng: 74.8723 },
            'darjeeling': { lat: 27.0410, lng: 88.2663 },
            'mysore': { lat: 12.2958, lng: 76.6394 },
            'lucknow': { lat: 26.8467, lng: 80.9462 },
            'chandigarh': { lat: 30.7333, lng: 76.7794 },
            'srinagar': { lat: 34.0837, lng: 74.7973 },
            'guwahati': { lat: 26.1445, lng: 91.7362 },
            'indore': { lat: 22.7196, lng: 75.8577 },
            'bhopal': { lat: 23.1815, lng: 79.9864 },
            'patna': { lat: 25.5941, lng: 85.1376 },
            'ranchi': { lat: 23.3441, lng: 85.3096 },
            'raipur': { lat: 21.2514, lng: 81.6296 },
            'bhubaneswar': { lat: 20.2961, lng: 85.8245 },
            'thiruvananthapuram': { lat: 8.5241, lng: 76.9366 },
            'visakhapatnam': { lat: 17.6868, lng: 83.2185 },
            'surat': { lat: 21.1702, lng: 72.8311 },
            'kanpur': { lat: 26.4499, lng: 80.3319 },
            'nagpur': { lat: 21.1458, lng: 79.0882 },
            'coimbatore': { lat: 11.0168, lng: 76.9558 },
            'madurai': { lat: 9.9252, lng: 78.1198 },
            'jodhpur': { lat: 26.2389, lng: 73.0243 },
            'dehradun': { lat: 30.3165, lng: 78.0322 },
            'pondicherry': { lat: 11.9416, lng: 79.8083 },

            // Specific Travel Spots (Full Names)
            'goa beach': { lat: 15.2993, lng: 74.1240 },
            'manali hill station': { lat: 32.2396, lng: 77.1887 },
            'kerala backwaters': { lat: 9.4981, lng: 76.3388 },
            'jaipur city tour': { lat: 26.9124, lng: 75.7873 },
            'leh ladakh mountain': { lat: 34.1526, lng: 77.5770 },
            'ooty hill station': { lat: 11.4102, lng: 76.6955 },
            'varanasi spiritual': { lat: 25.3176, lng: 82.9739 },
            'mumbai night life': { lat: 19.0760, lng: 72.8777 },
            'shimla snow mountain': { lat: 31.1048, lng: 77.1734 },
            'rishikesh yoga': { lat: 30.0869, lng: 78.2676 },
            'tirupathi spiritual temple': { lat: 13.6288, lng: 79.4192 },
            'agra taj mahal': { lat: 27.1767, lng: 78.0081 },
            'mysore palace': { lat: 12.2958, lng: 76.6394 },
            'darjeeling tea gardens': { lat: 27.0410, lng: 88.2663 },
            'munnar hill station': { lat: 10.0889, lng: 77.0595 },
            'pushkar desert': { lat: 26.4897, lng: 74.5511 },
            'alleppey houseboat': { lat: 9.4981, lng: 76.3388 },
            'gulmarg kashmir': { lat: 34.0484, lng: 74.3805 },
            'hampi ancient ruins': { lat: 15.3350, lng: 76.4600 },
            'sikkim mountains': { lat: 27.3314, lng: 88.6138 },
            'ranthambore tiger reserve': { lat: 26.0173, lng: 76.5026 },
            'khajuraho temples': { lat: 24.8318, lng: 79.9199 },
            'coorg coffee plantations': { lat: 12.3375, lng: 75.8069 },
            'udaipur palace city': { lat: 24.5854, lng: 73.7125 },
            'maldives island getaway': { lat: 3.2028, lng: 73.2207 },
            'jaisalmer desert camp': { lat: 26.9157, lng: 70.9083 },
            'andaman nicobar islands': { lat: 11.6234, lng: 92.7265 },
            'spiti valley': { lat: 32.2276, lng: 78.0710 },
            'pondicherry french colony': { lat: 11.9416, lng: 79.8083 },
            'mahabalipuram temples': { lat: 12.6208, lng: 80.1945 },
            'kaziranga national park': { lat: 26.5775, lng: 93.1711 },
            'mount abu hill station': { lat: 24.5926, lng: 72.7156 },
            'ajanta ellora caves': { lat: 20.5519, lng: 75.7033 },
            'nainital lake city': { lat: 29.3919, lng: 79.4542 },
            'konark sun temple': { lat: 19.8876, lng: 86.0945 },

            // Short Names (First Word Fallback)
            'tirupathi': { lat: 13.6288, lng: 79.4192 },
            'munnar': { lat: 10.0889, lng: 77.0595 },
            'gulmarg': { lat: 34.0484, lng: 74.3805 },
            'alleppey': { lat: 9.4981, lng: 76.3388 },
            'coorg': { lat: 12.3375, lng: 75.8069 },
            'hampi': { lat: 15.3350, lng: 76.4600 },
            'khajuraho': { lat: 24.8318, lng: 79.9199 },
            'pushkar': { lat: 26.4897, lng: 74.5511 },
            'sikkim': { lat: 27.3314, lng: 88.6138 },
            'ranthambore': { lat: 26.0173, lng: 76.5026 },
            'maldives': { lat: 3.2028, lng: 73.2207 },
            'jaisalmer': { lat: 26.9157, lng: 70.9083 },
            'andaman': { lat: 11.6234, lng: 92.7265 },
            'spiti': { lat: 32.2276, lng: 78.0710 },
            'pondicherry': { lat: 11.9416, lng: 79.8083 },
            'mahabalipuram': { lat: 12.6208, lng: 80.1945 },
            'kaziranga': { lat: 26.5775, lng: 93.1711 },
            'mount': { lat: 24.5926, lng: 72.7156 },
            'ajanta': { lat: 20.5519, lng: 75.7033 },
            'nainital': { lat: 29.3919, lng: 79.4542 },
            'konark': { lat: 19.8876, lng: 86.0945 }
        };
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.checkUserLocation();
        this.loadPopularDestinations();
    }

    checkUserLocation() {
        if (!this.userLocation) {
            this.showLocationModal();
        } else {
            this.updateLocationDisplay();
        }
    }

    showLocationModal() {
        const modal = document.getElementById('locationModal');
        if (modal) {
            modal.classList.add('show');
        }
    }

    hideLocationModal() {
        const modal = document.getElementById('locationModal');
        if (modal) {
            modal.classList.remove('show');
        }
    }

    setUserLocation() {
        const input = document.getElementById('userLocation');
        const location = input.value.trim();

        if (!location) {
            alert('Please enter a location');
            return;
        }

        this.userLocation = location;
        localStorage.setItem('userLocation', location);
        this.updateLocationDisplay();
        this.hideLocationModal();
        input.value = '';

        // Reload if there are current results
        const results = document.getElementById('results');
        if (results && results.innerHTML) {
            const query = document.getElementById('queryInput').value;
            if (query) {
                this.handleSearch();
            }
        }

        // Also reload popular destinations to show distance
        this.loadPopularDestinations();
    }

    updateLocationDisplay() {
        const locationElement = document.getElementById('currentLocation');
        if (locationElement) {
            locationElement.textContent = this.userLocation || 'Not Set';
        }
    }

    setupEventListeners() {
        const searchForm = document.getElementById('searchForm');
        if (searchForm) {
            searchForm.addEventListener('submit', (e) => {
                e.preventDefault();
                this.handleSearch();
            });
        }

        const modal = document.getElementById('locationModal');
        if (modal) {
            modal.addEventListener('click', (e) => {
                if (e.target === modal) {
                    this.hideLocationModal();
                }
            });
        }

        // Allow Enter to submit location
        const locationInput = document.getElementById('userLocation');
        if (locationInput) {
            locationInput.addEventListener('keypress', (e) => {
                if (e.key === 'Enter') {
                    this.setUserLocation();
                }
            });
        }
    }

    calculateDistance(userLoc, destName) {
        // Get user coordinates
        const userKey = userLoc.toLowerCase().trim();
        const userCoords = this.locationCoordinates[userKey];

        if (!userCoords) {
            return null;
        }

        // Get destination coordinates
        // First try exact match
        let destKey = destName.toLowerCase().trim();
        let destCoords = this.locationCoordinates[destKey];

        // If not found, try first word (fallback for generic cities)
        if (!destCoords) {
            destKey = destName.split(' ')[0].toLowerCase();
            destCoords = this.locationCoordinates[destKey];
        }

        if (!destCoords) {
            return null;
        }

        // Haversine formula for distance calculation
        const R = 6371; // Earth's radius in km
        const dLat = (destCoords.lat - userCoords.lat) * Math.PI / 180;
        const dLng = (destCoords.lng - userCoords.lng) * Math.PI / 180;
        const a = Math.sin(dLat / 2) * Math.sin(dLat / 2) +
            Math.cos(userCoords.lat * Math.PI / 180) *
            Math.cos(destCoords.lat * Math.PI / 180) *
            Math.sin(dLng / 2) * Math.sin(dLng / 2);
        const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
        const distance = R * c;

        return Math.round(distance);
    }

    async loadPopularDestinations() {
        try {
            const response = await fetch(`${this.baseURL}/api/all-spots`);
            if (!response.ok) throw new Error('Failed to load spots');

            const data = await response.json();
            const spots = data.spots || [];

            // Sort by rating (highest first) and take top 3
            const popularSpots = spots
                .sort((a, b) => b.rating - a.rating)
                .slice(0, 3);

            this.displayPopularSpots(popularSpots);
        } catch (error) {
            console.error('Error loading popular destinations:', error);
        }
    }

    displayPopularSpots(spots) {
        const container = document.getElementById('popularGrid');
        if (!container) return;

        container.innerHTML = spots.map(spot => this.createCardHTML(spot, false)).join('');
    }

    async handleSearch() {
        const query = document.getElementById('queryInput').value.trim();

        if (!query) {
            this.showError('Please enter a search query');
            return;
        }

        this.showLoading(true);

        // Hide popular section when searching
        const popularSection = document.getElementById('popularDestinations');
        if (popularSection) popularSection.style.display = 'none';

        try {
            const recommendations = await this.getRecommendations(query);
            this.currentResults = recommendations; // Store for sorting
            this.handleSort(); // Display sorted results
        } catch (error) {
            console.error('Error:', error);
            this.showError('Error fetching recommendations. Please check if the backend server is running.');
        } finally {
            this.showLoading(false);
        }
    }

    async getRecommendations(query, topK = 10) {
        // Call Python backend to get recommendations
        const response = await fetch(`${this.baseURL}/api/recommend`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ query: query, top_k: topK })
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();
        return data.recommendations || [];
    }

    handleSort() {
        const sortValue = document.getElementById('sortBy').value;
        let sortedResults = [...this.currentResults];

        switch (sortValue) {
            case 'price_low':
                sortedResults.sort((a, b) => a.budget_min - b.budget_min);
                break;
            case 'price_high':
                sortedResults.sort((a, b) => b.budget_min - a.budget_min);
                break;
            case 'rating':
                sortedResults.sort((a, b) => b.rating - a.rating);
                break;
            case 'distance':
                if (this.userLocation) {
                    sortedResults.sort((a, b) => {
                        const distA = this.calculateDistance(this.userLocation, a.name) || Infinity;
                        const distB = this.calculateDistance(this.userLocation, b.name) || Infinity;
                        return distA - distB;
                    });
                }
                break;
            default: // relevance
                sortedResults.sort((a, b) => b.relevance_score - a.relevance_score);
        }

        this.displayResults(sortedResults);
    }

    createCardHTML(rec, showScore = true) {
        // Calculate distance from user location
        let distanceInfo = '';

        if (this.userLocation) {
            const calculatedDistance = this.calculateDistance(this.userLocation, rec.name);
            if (calculatedDistance) {
                distanceInfo = `<div class="detail-badge highlight">
                    <span class="detail-label">📍 Distance</span>
                    <span class="detail-value">${calculatedDistance} km</span>
                </div>`;
            }
        }

        // Format best months
        const bestMonths = rec.best_months && rec.best_months.length > 0
            ? rec.best_months.map(m => this.capitalizeFirst(m)).join(', ')
            : 'Year-round';

        const scoreBadge = showScore
            ? `<span class="score-badge" title="Relevance Score">🎯 ${(rec.relevance_score * 100).toFixed(1)}%</span>`
            : `<span class="score-badge">⭐ ${rec.rating}/5.0</span>`;

        const scoreDetail = showScore
            ? `<div class="detail-badge highlight-score">
                <span class="detail-label">📊 Relevance Score</span>
                <span class="detail-value">${(rec.relevance_score * 100).toFixed(1)}%</span>
               </div>`
            : '';

        return `
            <div class="result-card">
                <div class="card-header">
                    <span class="rank-badge">#${rec.rank || 'Top'}</span>
                    <h3 class="destination-name">${rec.name}</h3>
                    ${scoreBadge}
                </div>

                <div class="card-details">
                    ${scoreDetail}
                    <div class="detail-badge">
                        <span class="detail-label">💰 Budget</span>
                        <span class="detail-value">${rec.budget_range}</span>
                    </div>
                    <div class="detail-badge">
                        <span class="detail-label">🎯 Mood</span>
                        <span class="detail-value">${rec.moods.join(', ')}</span>
                    </div>
                    <div class="detail-badge">
                        <span class="detail-label">⏱️ Duration</span>
                        <span class="detail-value">${rec.duration_days} days</span>
                    </div>
                    <div class="detail-badge">
                        <span class="detail-label">📅 Best Time</span>
                        <span class="detail-value">${bestMonths}</span>
                    </div>
                    ${distanceInfo}
                    <div class="detail-badge">
                        <span class="detail-label">⭐ Rating</span>
                        <span class="detail-value">${rec.rating}/5.0</span>
                    </div>
                </div>

                <div class="card-description">
                    ${rec.description}
                </div>
            </div>
        `;
    }

    displayResults(recommendations) {
        const resultsContainer = document.getElementById('results');
        const noResults = document.getElementById('noResults');
        const resultsHeader = document.getElementById('resultsHeader');

        if (!recommendations || recommendations.length === 0) {
            resultsContainer.innerHTML = '';
            noResults.classList.add('active');
            if (resultsHeader) resultsHeader.style.display = 'none';
            return;
        }

        noResults.classList.remove('active');
        if (resultsHeader) resultsHeader.style.display = 'flex';

        resultsContainer.innerHTML = recommendations.map(rec => this.createCardHTML(rec)).join('');
    }

    showLoading(show) {
        const loading = document.getElementById('loading');
        if (loading) {
            if (show) {
                loading.classList.add('active');
            } else {
                loading.classList.remove('active');
            }
        }
    }

    showError(message) {
        const resultsContainer = document.getElementById('results');
        const resultsHeader = document.getElementById('resultsHeader');

        if (resultsHeader) resultsHeader.style.display = 'none';

        if (resultsContainer) {
            resultsContainer.innerHTML = `
                <div style="color: #f87171; padding: 40px; text-align: center; background: rgba(239, 68, 68, 0.1); border-radius: 16px; border: 1px solid rgba(239, 68, 68, 0.3);">
                    <div style="font-size: 3rem; margin-bottom: 15px;">⚠️</div>
                    <div style="font-size: 1.1rem; font-weight: 600;">${message}</div>
                </div>
            `;
        }
        const noResults = document.getElementById('noResults');
        if (noResults) {
            noResults.classList.remove('active');
        }
    }

    capitalizeFirst(str) {
        if (!str) return '';
        return str.charAt(0).toUpperCase() + str.slice(1);
    }
}

// Initialize app when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.app = new TravelRecommendationApp();
});