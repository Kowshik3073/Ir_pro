// Travel Spot Recommendation System - Frontend
// Connects to Python backend for recommendations

class TravelRecommendationApp {
    constructor() {
        this.baseURL = 'http://localhost:8001'; // Python server URL
        this.userLocation = localStorage.getItem('userLocation') || null;
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
            'bhopal': { lat: 23.1815, lng: 79.9864 }
        };
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.checkUserLocation();
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

    handleQueryKeydown(event) {
        // Enter key submits form
        if (event.key === 'Enter' && !event.shiftKey) {
            event.preventDefault();
            this.handleSearch();
        }
        // Shift+Enter adds newline (default behavior)
    }

    calculateDistance(userLoc, destName) {
        // Get user coordinates
        const userKey = userLoc.toLowerCase();
        const userCoords = this.locationCoordinates[userKey];

        if (!userCoords) {
            return null;
        }

        // Get destination coordinates (use first word of destination name)
        const destKey = destName.split(' ')[0].toLowerCase();
        const destCoords = this.locationCoordinates[destKey];

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

    async handleSearch() {
        const query = document.getElementById('queryInput').value.trim();
        
        if (!query) {
            this.showError('Please enter a search query');
            return;
        }

        this.showLoading(true);
        
        try {
            const recommendations = await this.getRecommendations(query);
            this.displayResults(recommendations, query);
        } catch (error) {
            console.error('Error:', error);
            this.showError('Error fetching recommendations. Please check if the backend server is running.');
        } finally {
            this.showLoading(false);
        }
    }

    async getRecommendations(query, topK = 5) {
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

    displayResults(recommendations, query) {
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
        if (resultsHeader) resultsHeader.style.display = 'block';

        resultsContainer.innerHTML = recommendations.map((rec, index) => {
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

            return `
                <div class="result-card">
                    <div class="card-header">
                        <span class="rank-badge">#${rec.rank}</span>
                        <h3 class="destination-name">${rec.name}</h3>
                    </div>

                    <div class="card-details">
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
        }).join('');
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