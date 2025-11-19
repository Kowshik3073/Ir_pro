/**
 * All Places Page - Display all travel destinations with distance calculation
 */

class AllPlacesApp {
    constructor() {
        this.userLocation = null;
        this.allSpots = [];
        this.placeToDelete = null;
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
        const locationModal = document.getElementById('locationModal');
        if (locationModal) {
            locationModal.addEventListener('click', (e) => {
                if (e.target === locationModal) {
                    this.hideLocationModal();
                }
            });
        }

        const addPlaceModal = document.getElementById('addPlaceModal');
        if (addPlaceModal) {
            addPlaceModal.addEventListener('click', (e) => {
                if (e.target === addPlaceModal) {
                    this.closeAddPlaceModal();
                }
            });
        }

        const confirmDeleteModal = document.getElementById('confirmDeleteModal');
        if (confirmDeleteModal) {
            confirmDeleteModal.addEventListener('click', (e) => {
                if (e.target === confirmDeleteModal) {
                    this.closeDeleteModal();
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

        // Escape key to close modals
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') {
                const addPlaceModal = document.getElementById('addPlaceModal');
                const confirmDeleteModal = document.getElementById('confirmDeleteModal');
                const locationModal = document.getElementById('locationModal');
                
                if (addPlaceModal && addPlaceModal.classList.contains('show')) {
                    this.closeAddPlaceModal();
                } else if (confirmDeleteModal && confirmDeleteModal.classList.contains('show')) {
                    this.closeDeleteModal();
                } else if (locationModal && locationModal.classList.contains('show')) {
                    this.hideLocationModal();
                }
            }
        });
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
            const response = await fetch('http://localhost:8001/api/all-spots');
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
        const loading = document.getElementById('loading');
        const noResults = document.getElementById('noResults');
        
        if (!grid) return;

        grid.innerHTML = '';
        
        if (loading) loading.classList.remove('active');
        
        if (this.allSpots.length === 0) {
            noResults.classList.add('active');
            return;
        }

        noResults.classList.remove('active');

        // Sort spots by rating (highest first)
        const sortedSpots = [...this.allSpots].sort((a, b) => b.rating - a.rating);

        sortedSpots.forEach((spot, index) => {
            const distance = this.userLocation ? 
                this.calculateDistance(this.userLocation, spot.name) : null;
            
            const card = document.createElement('div');
            card.className = 'place-card';
            
            let distanceHtml = '';
            if (distance !== null) {
                distanceHtml = `<div class="detail-badge highlight">
                    <span class="detail-label">📍 Distance</span>
                    <span class="detail-value">${distance} km</span>
                </div>`;
            }

            // Format best months
            const bestMonths = spot.best_months && spot.best_months.length > 0 
                ? spot.best_months.slice(0, 3).map(m => this.capitalizeFirst(m)).join(', ')
                : 'Year-round';
            
            card.innerHTML = `
                <button class="delete-btn" onclick="allPlacesApp.showDeleteModal(${spot.id}, '${spot.name}')">✕</button>
                <div class="card-header">
                    <h3 class="place-name">${spot.name}</h3>
                    <div class="rating-badge">⭐ ${spot.rating}</div>
                </div>
                
                <div class="moods-container">
                    ${spot.moods.map(mood => `<span class="mood-tag">${mood}</span>`).join('')}
                </div>
                
                <div class="card-details">
                    <div class="detail-badge">
                        <span class="detail-label">💰 Budget</span>
                        <span class="detail-value">${spot.budget}</span>
                    </div>
                    <div class="detail-badge">
                        <span class="detail-label">⏱️ Duration</span>
                        <span class="detail-value">${spot.duration}</span>
                    </div>
                    <div class="detail-badge">
                        <span class="detail-label">📅 Best Time</span>
                        <span class="detail-value">${bestMonths}</span>
                    </div>
                    ${distanceHtml}
                </div>
            `;
            
            grid.appendChild(card);
        });
    }    calculateDistance(userCity, destinationName) {
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
        const loading = document.getElementById('loading');
        const noResults = document.getElementById('noResults');
        
        if (loading) loading.classList.remove('active');
        if (noResults) {
            noResults.classList.add('active');
            noResults.innerHTML = `
                <div class="no-results-icon">⚠️</div>
                <p class="no-results-text">${message}</p>
            `;
        }
    }    capitalizeFirst(str) {
        if (!str) return '';
        return str.charAt(0).toUpperCase() + str.slice(1);
    }

    showAddPlaceModal() {
        const modal = document.getElementById('addPlaceModal');
        if (modal) {
            modal.classList.add('show');
            document.getElementById('addPlaceForm').reset();
            // Focus on first input for better UX
            document.getElementById('placeName').focus();
        }
    }

    closeAddPlaceModal() {
        const modal = document.getElementById('addPlaceModal');
        if (modal) {
            modal.classList.remove('show');
            document.getElementById('addPlaceForm').reset();
            this.clearFormErrors();
        }
    }

    clearFormErrors() {
        const form = document.getElementById('addPlaceForm');
        if (form) {
            form.querySelectorAll('.form-group').forEach(group => {
                group.classList.remove('error');
            });
        }
    }

    showFormError(fieldId, message) {
        const field = document.getElementById(fieldId);
        if (field) {
            const group = field.closest('.form-group');
            if (group) {
                group.classList.add('error');
                let errorEl = group.querySelector('.form-error');
                if (!errorEl) {
                    errorEl = document.createElement('div');
                    errorEl.className = 'form-error';
                    group.appendChild(errorEl);
                }
                errorEl.textContent = message;
            }
        }
    }

    validateAddPlaceForm() {
        this.clearFormErrors();
        let isValid = true;

        const name = document.getElementById('placeName').value.trim();
        const moods = document.getElementById('placeMoods').value.trim();
        const desc = document.getElementById('placeDescription').value.trim();
        const budgetMin = parseInt(document.getElementById('budgetMin').value);
        const budgetMax = parseInt(document.getElementById('budgetMax').value);
        const duration = parseInt(document.getElementById('duration').value);
        const distance = parseInt(document.getElementById('distance').value);
        const rating = parseFloat(document.getElementById('rating').value);

        if (!name) {
            this.showFormError('placeName', 'Place name is required');
            isValid = false;
        } else if (name.length < 3) {
            this.showFormError('placeName', 'Place name must be at least 3 characters');
            isValid = false;
        }

        if (!moods) {
            this.showFormError('placeMoods', 'At least one mood is required');
            isValid = false;
        }

        if (!desc) {
            this.showFormError('placeDescription', 'Description is required');
            isValid = false;
        } else if (desc.length < 20) {
            this.showFormError('placeDescription', 'Description must be at least 20 characters');
            isValid = false;
        }

        if (isNaN(budgetMin) || budgetMin < 0) {
            this.showFormError('budgetMin', 'Valid budget min required');
            isValid = false;
        }

        if (isNaN(budgetMax) || budgetMax < budgetMin) {
            this.showFormError('budgetMax', 'Max budget must be >= min budget');
            isValid = false;
        }

        if (isNaN(duration) || duration < 1) {
            this.showFormError('duration', 'Duration must be at least 1 day');
            isValid = false;
        }

        if (isNaN(distance) || distance < 0) {
            this.showFormError('distance', 'Valid distance required');
            isValid = false;
        }

        if (isNaN(rating) || rating < 0 || rating > 5) {
            this.showFormError('rating', 'Rating must be between 0-5');
            isValid = false;
        }

        return isValid;
    }

    async submitAddPlace(event) {
        event.preventDefault();

        // Validate form
        if (!this.validateAddPlaceForm()) {
            return;
        }

        const form = document.getElementById('addPlaceForm');
        const submitBtn = form.querySelector('.form-btn.submit');
        const originalText = submitBtn.textContent;
        submitBtn.disabled = true;
        submitBtn.textContent = '⏳ Adding...';

        const newPlace = {
            name: document.getElementById('placeName').value.trim(),
            mood: document.getElementById('placeMoods').value.split(',').map(m => m.trim()),
            description: document.getElementById('placeDescription').value.trim(),
            budget_min: parseInt(document.getElementById('budgetMin').value),
            budget_max: parseInt(document.getElementById('budgetMax').value),
            duration_days: parseInt(document.getElementById('duration').value),
            distance_km: parseInt(document.getElementById('distance').value),
            rating: parseFloat(document.getElementById('rating').value),
            best_months: document.getElementById('bestMonths').value 
                ? document.getElementById('bestMonths').value.split(',').map(m => m.trim())
                : []
        };

        try {
            const response = await fetch('http://localhost:8001/api/add-place', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(newPlace)
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            // Success feedback
            submitBtn.textContent = '✅ Added!';
            submitBtn.style.background = 'linear-gradient(135deg, #10b981, #059669)';
            
            setTimeout(() => {
                this.closeAddPlaceModal();
                submitBtn.disabled = false;
                submitBtn.textContent = originalText;
                submitBtn.style.background = '';
                // Reload places
                this.loadAllSpots().then(() => this.displayAllPlaces());
            }, 1000);
        } catch (error) {
            console.error('Error adding place:', error);
            submitBtn.disabled = false;
            submitBtn.textContent = originalText;
            alert('❌ Error adding place. Please try again.');
        }
    }

    showDeleteModal(placeId, placeName) {
        this.placeToDelete = { id: placeId, name: placeName };
        const modal = document.getElementById('confirmDeleteModal');
        const text = document.getElementById('confirmDeleteText');
        if (modal && text) {
            text.textContent = `Are you sure you want to delete "${placeName}"? This action cannot be undone.`;
            modal.classList.add('show');
        }
    }

    closeDeleteModal() {
        const modal = document.getElementById('confirmDeleteModal');
        if (modal) {
            modal.classList.remove('show');
            this.placeToDelete = null;
        }
    }

    async confirmDelete() {
        if (!this.placeToDelete) return;

        try {
            const response = await fetch(`http://localhost:8001/api/remove-place/${this.placeToDelete.id}`, {
                method: 'DELETE'
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            alert(`✅ "${this.placeToDelete.name}" has been deleted!`);
            this.closeDeleteModal();
            await this.loadAllSpots();
            this.displayAllPlaces();
        } catch (error) {
            console.error('Error deleting place:', error);
            alert('❌ Error deleting place. Please try again.');
        }
    }
}

// Initialize app when page loads
document.addEventListener('DOMContentLoaded', () => {
    window.allPlacesApp = new AllPlacesApp();
});