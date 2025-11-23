
class AllPlacesApp {
    constructor() {
        this.baseURL = '';
        this.allSpots = [];
        this.init();
    }

    async init() {
        await this.loadSpots();
    }

    async loadSpots() {
        try {
            const response = await fetch(`${this.baseURL}/api/all-spots`);
            if (!response.ok) throw new Error('Failed to load spots');

            const data = await response.json();
            this.allSpots = data.spots || [];

            // Initial render
            this.applyFilters();
        } catch (error) {
            console.error('Error loading spots:', error);
            document.getElementById('destinationsGrid').innerHTML =
                '<p style="color: #f87171; text-align: center; grid-column: 1/-1;">Failed to load destinations. Is the server running?</p>';
        }
    }

    applyFilters() {
        const moodFilter = document.getElementById('moodFilter').value;
        const sortBy = document.getElementById('sortBy').value;

        let filtered = [...this.allSpots];

        // Filter by mood
        if (moodFilter !== 'all') {
            filtered = filtered.filter(spot =>
                spot.moods.some(m => m.toLowerCase() === moodFilter)
            );
        }

        // Sort
        switch (sortBy) {
            case 'price_low':
                filtered.sort((a, b) => a.budget_min - b.budget_min);
                break;
            case 'price_high':
                filtered.sort((a, b) => b.budget_min - a.budget_min);
                break;
            case 'rating':
                filtered.sort((a, b) => b.rating - a.rating);
                break;
            case 'name':
                filtered.sort((a, b) => a.name.localeCompare(b.name));
                break;
        }

        this.render(filtered);
        this.updateStats(filtered.length);
    }

    updateStats(count) {
        const stats = document.getElementById('stats');
        if (stats) {
            stats.textContent = `Showing ${count} destination${count !== 1 ? 's' : ''}`;
        }
    }

    render(spots) {
        const container = document.getElementById('destinationsGrid');
        const noResults = document.getElementById('noResults');

        if (spots.length === 0) {
            container.innerHTML = '';
            noResults.classList.add('active');
            return;
        }

        noResults.classList.remove('active');
        container.innerHTML = spots.map(spot => this.createCardHTML(spot)).join('');
    }

    createCardHTML(spot) {
        const bestMonths = spot.best_months && spot.best_months.length > 0
            ? spot.best_months.slice(0, 3).map(m => this.capitalizeFirst(m)).join(', ') + (spot.best_months.length > 3 ? '...' : '')
            : 'Year-round';

        return `
            <div class="result-card" style="padding: 30px;">
                <div class="card-header" style="margin-bottom: 20px;">
                    <h3 class="destination-name" style="font-size: 1.5rem;">${spot.name}</h3>
                    <span class="score-badge">⭐ ${spot.rating}</span>
                </div>

                <div class="card-details" style="grid-template-columns: 1fr; gap: 12px; margin-bottom: 20px;">
                    <div class="detail-badge" style="padding: 12px;">
                        <span class="detail-label">💰 Budget</span>
                        <span class="detail-value" style="font-size: 1rem;">${spot.budget}</span>
                    </div>
                    <div class="detail-badge" style="padding: 12px;">
                        <span class="detail-label">🎯 Mood</span>
                        <span class="detail-value" style="font-size: 1rem;">${spot.moods.join(', ')}</span>
                    </div>
                </div>

                <p style="color: var(--text-secondary); font-size: 0.95rem; margin-bottom: 20px; display: -webkit-box; -webkit-line-clamp: 3; -webkit-box-orient: vertical; overflow: hidden;">
                    ${spot.description}
                </p>
                
                <div style="display: flex; justify-content: space-between; align-items: center; font-size: 0.9rem; color: var(--text-secondary); border-top: 1px solid var(--border); padding-top: 15px;">
                    <span>⏱️ ${spot.duration}</span>
                    <span>📅 ${bestMonths}</span>
                </div>
            </div>
        `;
    }

    capitalizeFirst(str) {
        if (!str) return '';
        return str.charAt(0).toUpperCase() + str.slice(1);
    }
}

document.addEventListener('DOMContentLoaded', () => {
    window.allPlacesApp = new AllPlacesApp();
});