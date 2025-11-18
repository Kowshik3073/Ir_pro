/**
 * All Places Page - Display all travel destinations with distance calculation
 */

class AllPlacesApp {
    constructor() {
        this.userLocation = null;
        this.allSpots = [];
        this.cityCoordinates = {
            'mumbai': { lat: 19.0760, lng: 72.8777 },
            'delhi': { lat: 28.7041, lng: 77.1025 },
            'bangalore': { lat: 12.9716, lng: 77.5946 },
            'kolkata': { lat: 22.5726, lng: 88.3639 },
            'hyderabad': { lat: 17.3850, lng: 78.4867 },
            'pune': { lat: 18.5204, lng: 73.8567 },
            'ahmedabad': { lat: 23.0225, lng: 72.5714 },
            'chennai': { lat: 13.0827, lng: 80.2707 },
            'jaipur': { lat: 26.9124, lng: 75.7873 },
            'lucknow': { lat: 26.8467, lng: 80.9462 },
            'chandigarh': { lat: 30.7333, lng: 76.7794 },
            'srinagar': { lat: 34.0837, lng: 74.7973 },
            'guwahati': { lat: 26.1445, lng: 91.7362 },
            'kochi': { lat: 9.9312, lng: 76.2673 },
            'indore': { lat: 22.7196, lng: 75.8577 },
            'bhopal': { lat: 23.1815, lng: 79.9864 },
            'goa': { lat: 15.4909, lng: 73.8278 },
            'manali': { lat: 32.2392, lng: 77.1892 },
            'shimla': { lat: 31.1048, lng: 77.1734 },
            'ooty': { lat: 11.4102, lng: 76.6955 },
            'kerala': { lat: 10.8505, lng: 76.2711 },
            'leh': { lat: 34.1526, lng: 77.5770 },
            'varanasi': { lat: 25.3200, lng: 82.9850 },
            'rishikesh': { lat: 30.0889, lng: 78.2676 },
            'udaipur': { lat: 24.5854, lng: 73.7125 },
            'agra': { lat: 27.1767, lng: 78.0081 },
            'amritsar': { lat: 31.6340, lng: 74.8723 },
            'darjeeling': { lat: 27.0410, lng: 88.2663 },
            'mysore': { lat: 12.2958, lng: 76.6394 }
        };
        
        this.init();
    }

    async init() {
        // Load user location from localStorage
        this.loadUserLocation();
        
        // Load all spots from backend
        await this.loadAllSpots();
        
        // Display spots
        this.displayAllPlaces();
        
        // Setup event listeners
        this.setupEventListeners();
    }

    setupEventListeners() {
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

    loadUserLocation() {
        const saved = localStorage.getItem('userLocation');
        if (saved) {
            this.userLocation = saved;
            const locationElement = document.getElementById('currentLocation');
            if (locationElement) {
                locationElement.textContent = this.userLocation;
            }
        }
    }

    async loadAllSpots() {
        try {
            const response = await fetch('http://localhost:8000/api/all-spots');
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            const data = await response.json();
            this.allSpots = data.spots || [];
        } catch (error) {
            console.error('Error loading spots:', error);
            this.allSpots = [];
            this.showError('Error loading destinations. Please check if the backend server is running.');
        }
    }

    displayAllPlaces() {
        const grid = document.getElementById('allPlacesGrid');
        if (!grid) return;

        grid.innerHTML = '';
        
        if (this.allSpots.length === 0) {
            grid.innerHTML = '<p class="no-results">No destinations available. Please check backend connection.</p>';
            return;
        }

        // Sort spots by rating (highest first)
        const sortedSpots = [...this.allSpots].sort((a, b) => b.rating - a.rating);

        sortedSpots.forEach((spot) => {
            const distance = this.userLocation ? 
                this.calculateDistance(this.userLocation, spot.name) : null;
            
            const card = document.createElement('div');
            card.className = 'all-place-card';
            
            let distanceHtml = '';
            if (distance !== null) {
                distanceHtml = `<div class="distance-info">📍 ${distance} km away</div>`;
            }

            // Format best months
            const bestMonths = spot.best_months && spot.best_months.length > 0 
                ? spot.best_months.slice(0, 3).map(m => this.capitalizeFirst(m)).join(', ')
                : 'Year-round';
            
            card.innerHTML = `
                <div class="card-content">
                    <div class="card-rating">⭐ ${spot.rating}</div>
                    <h3>${spot.name}</h3>
                    <div class="card-moods">
                        ${spot.moods.map(mood => `<span class="mood-tag">${mood}</span>`).join('')}
                    </div>
                    <div class="card-details">
                        <div class="detail-item">💰 ${spot.budget}</div>
                        <div class="detail-item">⏰ ${spot.duration}</div>
                        <div class="detail-item">📅 Best: ${bestMonths}</div>
                        ${distanceHtml}
                    </div>
                </div>
            `;
            
            grid.appendChild(card);
        });
    }

    calculateDistance(userCity, destinationName) {
        const userCoords = this.cityCoordinates[userCity.toLowerCase()];
        if (!userCoords) return null;

        // Extract destination from name
        const destCity = this.getDestinationCity(destinationName);
        const destCoords = this.cityCoordinates[destCity.toLowerCase()];
        
        if (!destCoords) return null;

        // Haversine formula
        const R = 6371; // Earth's radius in km
        const lat1 = userCoords.lat * Math.PI / 180;
        const lat2 = destCoords.lat * Math.PI / 180;
        const deltaLat = (destCoords.lat - userCoords.lat) * Math.PI / 180;
        const deltaLng = (destCoords.lng - userCoords.lng) * Math.PI / 180;

        const a = Math.sin(deltaLat / 2) * Math.sin(deltaLat / 2) +
                  Math.cos(lat1) * Math.cos(lat2) * 
                  Math.sin(deltaLng / 2) * Math.sin(deltaLng / 2);
        
        const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
        const distance = R * c;

        return Math.round(distance);
    }

    getDestinationCity(destinationName) {
        // Map destination names to cities
        const mapping = {
            'manali': 'manali',
            'goa': 'goa',
            'kerala': 'kerala',
            'kochi': 'kochi',
            'leh': 'leh',
            'ooty': 'ooty',
            'shimla': 'shimla',
            'rishikesh': 'rishikesh',
            'jaipur': 'jaipur',
            'varanasi': 'varanasi',
            'mumbai': 'mumbai',
            'delhi': 'delhi',
            'bangalore': 'bangalore',
            'udaipur': 'udaipur',
            'agra': 'agra',
            'amritsar': 'amritsar',
            'darjeeling': 'darjeeling',
            'mysore': 'mysore'
        };
        
        const name = destinationName.toLowerCase();
        for (const [key, city] of Object.entries(mapping)) {
            if (name.includes(key)) {
                return city;
            }
        }
        return 'delhi'; // Default fallback
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
            alert('Please enter a city name');
            return;
        }

        this.userLocation = location;
        localStorage.setItem('userLocation', location);
        
        const locationElement = document.getElementById('currentLocation');
        if (locationElement) {
            locationElement.textContent = location;
        }
        
        this.hideLocationModal();
        input.value = '';
        
        // Refresh display with new distances
        this.displayAllPlaces();
    }

    showError(message) {
        const grid = document.getElementById('allPlacesGrid');
        if (grid) {
            grid.innerHTML = `
                <div style="grid-column: 1/-1; color: #FF6B6B; padding: 40px; text-align: center; background: var(--card-bg); border-radius: 12px; border: 1px solid var(--border-color);">
                    ${message}
                </div>
            `;
        }
    }

    capitalizeFirst(str) {
        if (!str) return '';
        return str.charAt(0).toUpperCase() + str.slice(1);
    }
}

// Initialize app when page loads
document.addEventListener('DOMContentLoaded', () => {
    window.allPlacesApp = new AllPlacesApp();
});