/**
 * Interactive Movie Recommendation System - Frontend JavaScript
 * Handles user interactions, API calls, and dynamic content updates
 */

class MovieRecommender {
    constructor() {
        this.apiBase = '/api';
        this.currentQuery = '';
        this.autocompleteTimeout = null;
        
        this.initializeElements();
        this.bindEvents();
        this.loadStats();
    }
    
    /**
     * Initialize DOM elements for easy access
     */
    initializeElements() {
        // Input elements
        this.movieInput = document.getElementById('movieInput');
        this.searchBtn = document.getElementById('searchBtn');
        this.autocompleteDropdown = document.getElementById('autocompleteDropdown');
        
        // Filter elements
        this.toggleFiltersBtn = document.getElementById('toggleFilters');
        this.filtersContainer = document.getElementById('filtersContainer');
        this.languageFilter = document.getElementById('languageFilter');
        this.genreFilter = document.getElementById('genreFilter');
        this.ratingFilter = document.getElementById('ratingFilter');
        this.applyFiltersBtn = document.getElementById('applyFilters');
        
        // Section elements
        this.loadingSection = document.getElementById('loadingSection');
        this.errorSection = document.getElementById('errorSection');
        this.resultsSection = document.getElementById('resultsSection');
        
        // Results elements
        this.resultsTitle = document.getElementById('resultsTitle');
        this.inputMovieTitle = document.getElementById('inputMovieTitle');
        this.movieGrid = document.getElementById('movieGrid');
        
        // Error elements
        this.errorText = document.getElementById('errorText');
        this.retryBtn = document.getElementById('retryBtn');
        
        // Stats elements
        this.totalMovies = document.getElementById('totalMovies');
        this.totalLanguages = document.getElementById('totalLanguages');
        this.avgRating = document.getElementById('avgRating');
        this.yearRange = document.getElementById('yearRange');
        
        // Modal elements
        this.modal = document.getElementById('modal');
        this.modalBody = document.getElementById('modalBody');
    }
    
    /**
     * Bind event listeners to interactive elements
     */
    bindEvents() {
        // Search functionality
        this.searchBtn.addEventListener('click', () => this.handleSearch());
        this.movieInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                this.handleSearch();
            }
        });
        
        // Autocomplete functionality
        this.movieInput.addEventListener('input', (e) => this.handleAutocomplete(e.target.value));
        this.movieInput.addEventListener('focus', () => this.showAutocomplete());
        this.movieInput.addEventListener('blur', () => {
            // Delay hiding to allow clicking on suggestions
            setTimeout(() => this.hideAutocomplete(), 200);
        });
        
        // Filter functionality
        this.toggleFiltersBtn.addEventListener('click', () => this.toggleFilters());
        this.applyFiltersBtn.addEventListener('click', () => this.applyFilters());
        
        // Error handling
        this.retryBtn.addEventListener('click', () => this.handleSearch());
        
        // Modal functionality
        document.addEventListener('click', (e) => {
            if (e.target === this.modal) {
                this.closeModal();
            }
        });
        
        // Keyboard shortcuts
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') {
                this.closeModal();
                this.hideAutocomplete();
            }
        });
    }
    
    /**
     * Handle movie search functionality
     */
    async handleSearch() {
        const movieTitle = this.movieInput.value.trim();
        
        if (!movieTitle) {
            this.showError('Please enter a movie title');
            return;
        }
        
        this.currentQuery = movieTitle;
        this.showLoading();
        
        try {
            const response = await fetch(`${this.apiBase}/recommend`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    movie_title: movieTitle,
                    num_recommendations: 10
                })
            });
            
            const data = await response.json();
            
            if (data.success) {
                this.showResults(data.recommendations, data.input_movie);
            } else {
                this.showError(data.error || 'Failed to get recommendations');
            }
            
        } catch (error) {
            console.error('Search error:', error);
            this.showError('Network error. Please check your connection and try again.');
        }
    }
    
    /**
     * Handle autocomplete suggestions
     */
    async handleAutocomplete(query) {
        if (this.autocompleteTimeout) {
            clearTimeout(this.autocompleteTimeout);
        }
        
        if (query.length < 2) {
            this.hideAutocomplete();
            return;
        }
        
        this.autocompleteTimeout = setTimeout(async () => {
            try {
                const response = await fetch(`${this.apiBase}/autocomplete?q=${encodeURIComponent(query)}&limit=5`);
                const data = await response.json();
                
                if (data.suggestions && data.suggestions.length > 0) {
                    this.showAutocompleteSuggestions(data.suggestions);
                } else {
                    this.hideAutocomplete();
                }
                
            } catch (error) {
                console.error('Autocomplete error:', error);
                this.hideAutocomplete();
            }
        }, 300); // Debounce for 300ms
    }
    
    /**
     * Show autocomplete suggestions
     */
    showAutocompleteSuggestions(suggestions) {
        this.autocompleteDropdown.innerHTML = '';
        
        suggestions.forEach(suggestion => {
            const item = document.createElement('div');
            item.className = 'autocomplete-item';
            item.textContent = suggestion;
            item.addEventListener('click', () => {
                this.movieInput.value = suggestion;
                this.hideAutocomplete();
                this.handleSearch();
            });
            this.autocompleteDropdown.appendChild(item);
        });
        
        this.showAutocomplete();
    }
    
    /**
     * Show autocomplete dropdown
     */
    showAutocomplete() {
        if (this.autocompleteDropdown.children.length > 0) {
            this.autocompleteDropdown.style.display = 'block';
        }
    }
    
    /**
     * Hide autocomplete dropdown
     */
    hideAutocomplete() {
        this.autocompleteDropdown.style.display = 'none';
    }
    
    /**
     * Toggle filters visibility
     */
    toggleFilters() {
        this.filtersContainer.classList.toggle('hidden');
        const isHidden = this.filtersContainer.classList.contains('hidden');
        this.toggleFiltersBtn.textContent = isHidden ? '🔧 Advanced Filters' : '🔧 Hide Filters';
    }
    
    /**
     * Apply filters to get filtered movies
     */
    async applyFilters() {
        const language = this.languageFilter.value;
        const genre = this.genreFilter.value;
        const minRating = this.ratingFilter.value ? parseFloat(this.ratingFilter.value) : null;
        
        if (!language && !genre && !minRating) {
            this.showError('Please select at least one filter');
            return;
        }
        
        this.showLoading();
        
        try {
            const response = await fetch(`${this.apiBase}/filter`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    language: language || null,
                    genre: genre || null,
                    min_rating: minRating
                })
            });
            
            const data = await response.json();
            
            if (data.success) {
                this.showFilteredResults(data.movies, { language, genre, minRating });
            } else {
                this.showError(data.error || 'Failed to get filtered movies');
            }
            
        } catch (error) {
            console.error('Filter error:', error);
            this.showError('Network error. Please check your connection and try again.');
        }
    }
    
    /**
     * Show loading state
     */
    showLoading() {
        this.hideAllSections();
        this.loadingSection.classList.remove('hidden');
        this.searchBtn.classList.add('loading');
    }
    
    /**
     * Show error message
     */
    showError(message) {
        this.hideAllSections();
        this.errorText.textContent = message;
        this.errorSection.classList.remove('hidden');
        this.searchBtn.classList.remove('loading');
    }
    
    /**
     * Show search results
     */
    showResults(recommendations, inputMovie) {
        this.hideAllSections();
        this.inputMovieTitle.textContent = inputMovie;
        this.resultsTitle.innerHTML = `🎯 Recommendations for "<span id="inputMovieTitle">${inputMovie}</span>"`;
        
        this.renderMovieCards(recommendations);
        this.resultsSection.classList.remove('hidden');
        this.searchBtn.classList.remove('loading');
        
        // Smooth scroll to results
        this.resultsSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
    
    /**
     * Show filtered results
     */
    showFilteredResults(movies, filters) {
        this.hideAllSections();
        
        const filterText = this.buildFilterText(filters);
        this.resultsTitle.innerHTML = `🔍 Movies matching: ${filterText}`;
        
        this.renderMovieCards(movies);
        this.resultsSection.classList.remove('hidden');
        this.searchBtn.classList.remove('loading');
        
        // Smooth scroll to results
        this.resultsSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
    
    /**
     * Build filter description text
     */
    buildFilterText(filters) {
        const parts = [];
        if (filters.language) parts.push(`Language: ${filters.language}`);
        if (filters.genre) parts.push(`Genre: ${filters.genre}`);
        if (filters.minRating) parts.push(`Rating: ${filters.minRating}+`);
        return parts.join(' | ');
    }
    
    /**
     * Render movie cards in the grid
     */
    renderMovieCards(movies) {
        this.movieGrid.innerHTML = '';
        
        if (movies.length === 0) {
            this.movieGrid.innerHTML = `
                <div class="no-results">
                    <h3>No movies found</h3>
                    <p>Try adjusting your search criteria or filters.</p>
                </div>
            `;
            return;
        }
        
        movies.forEach((movie, index) => {
            const movieCard = this.createMovieCard(movie);
            movieCard.style.animationDelay = `${index * 0.1}s`;
            movieCard.classList.add('fade-in');
            this.movieGrid.appendChild(movieCard);
        });
    }
    
    /**
     * Create individual movie card element
     */
    createMovieCard(movie) {
        const card = document.createElement('div');
        card.className = 'movie-card';
        
        // Handle poster image with fallback
        const posterUrl = movie.poster_url && movie.poster_url !== 'N/A' 
            ? movie.poster_url 
            : 'https://via.placeholder.com/300x450/333/fff?text=No+Poster';
        
        // Create meta badges
        const metaBadges = [];
        if (movie.year) metaBadges.push(`${movie.year}`);
        if (movie.rating) metaBadges.push(`⭐ ${movie.rating}`);
        if (movie.similarity_score) metaBadges.push(`${Math.round(movie.similarity_score * 100)}% match`);
        
        card.innerHTML = `
            <img src="${posterUrl}" alt="${movie.title}" class="movie-poster" 
                 onerror="this.src='https://via.placeholder.com/300x450/333/fff?text=No+Poster'">
            <div class="movie-info">
                <h3 class="movie-title">${movie.title}</h3>
                <div class="movie-meta">
                    ${metaBadges.map(badge => `<span class="meta-badge">${badge}</span>`).join('')}
                </div>
                <div class="movie-details">
                    <p><strong>Language:</strong> ${movie.language}</p>
                    <p><strong>Genres:</strong> ${movie.genres}</p>
                    <p><strong>Director:</strong> ${movie.director}</p>
                    <p><strong>Cast:</strong> ${movie.main_actors}</p>
                </div>
                ${movie.reason ? `
                    <div class="recommendation-reason">
                        <h4>🎯 Why recommended:</h4>
                        <p>${movie.reason}</p>
                    </div>
                ` : ''}
            </div>
        `;
        
        return card;
    }
    
    /**
     * Hide all main sections
     */
    hideAllSections() {
        this.loadingSection.classList.add('hidden');
        this.errorSection.classList.add('hidden');
        this.resultsSection.classList.add('hidden');
    }
    
    /**
     * Load and display dataset statistics
     */
    async loadStats() {
        try {
            const response = await fetch(`${this.apiBase}/stats`);
            const data = await response.json();
            
            if (data.success) {
                const stats = data.stats;
                this.totalMovies.textContent = stats.total_movies || '-';
                this.totalLanguages.textContent = Object.keys(stats.languages || {}).length || '-';
                this.avgRating.textContent = stats.average_rating || '-';
                this.yearRange.textContent = stats.year_range || '-';
            }
            
        } catch (error) {
            console.error('Stats loading error:', error);
        }
    }
    
    /**
     * Show modal with content
     */
    showModal(title, content) {
        this.modalBody.innerHTML = `
            <h2>${title}</h2>
            <div>${content}</div>
        `;
        this.modal.classList.remove('hidden');
        document.body.style.overflow = 'hidden';
    }
    
    /**
     * Close modal
     */
    closeModal() {
        this.modal.classList.add('hidden');
        document.body.style.overflow = 'auto';
    }
}

/**
 * Modal content functions
 */
function showAbout() {
    const content = `
        <p>The Indian Movie Recommender is an intelligent system that helps you discover your next favorite film from Bollywood and regional cinema.</p>
        <h3>🎯 How it works:</h3>
        <ul>
            <li><strong>TF-IDF Vectorization:</strong> Converts movie features into numerical vectors</li>
            <li><strong>Cosine Similarity:</strong> Measures similarity between movies based on genres, cast, director, and themes</li>
            <li><strong>Smart Matching:</strong> Handles partial titles and misspellings using fuzzy string matching</li>
            <li><strong>OMDb Integration:</strong> Fetches high-quality movie posters and additional metadata</li>
        </ul>
        <h3>🎬 Features:</h3>
        <ul>
            <li>Support for multiple Indian languages (Hindi, Tamil, Telugu, Kannada, Malayalam, Bengali, Marathi)</li>
            <li>Autocomplete suggestions as you type</li>
            <li>Advanced filtering by language, genre, and rating</li>
            <li>Detailed recommendation explanations</li>
            <li>Responsive design for all devices</li>
        </ul>
    `;
    movieRecommender.showModal('About Indian Movie Recommender', content);
}

function showHelp() {
    const content = `
        <h3>🔍 How to use:</h3>
        <ol>
            <li><strong>Search by Movie:</strong> Enter any movie title (e.g., "Dangal", "Baahubali", "3 Idiots")</li>
            <li><strong>Use Autocomplete:</strong> Start typing and select from suggestions</li>
            <li><strong>Apply Filters:</strong> Use advanced filters to discover movies by language, genre, or rating</li>
            <li><strong>View Results:</strong> Browse recommendations with posters, details, and explanations</li>
        </ol>
        <h3>💡 Tips:</h3>
        <ul>
            <li>Try movie titles in English or Indian languages</li>
            <li>Use partial titles - the system handles misspellings</li>
            <li>Explore different languages and genres using filters</li>
            <li>Check the recommendation reasons to understand why movies are suggested</li>
        </ul>
        <h3>🎭 Supported Languages:</h3>
        <p>Hindi, Tamil, Telugu, Kannada, Malayalam, Bengali, Marathi, and more!</p>
    `;
    movieRecommender.showModal('Help & Usage Guide', content);
}

function showContact() {
    const content = `
        <h3>📧 Get in Touch:</h3>
        <p>We'd love to hear from you! Whether you have feedback, suggestions, or need help, feel free to reach out.</p>
        <div style="margin: 2rem 0;">
            <p><strong>📧 Email:</strong> support@movierecommender.com</p>
            <p><strong>🐛 Report Issues:</strong> github.com/movierecommender/issues</p>
            <p><strong>💡 Feature Requests:</strong> github.com/movierecommender/discussions</p>
        </div>
        <h3>🤝 Contributing:</h3>
        <p>This is an open-source project! Contributions are welcome:</p>
        <ul>
            <li>Add more movies to the dataset</li>
            <li>Improve recommendation algorithms</li>
            <li>Enhance the user interface</li>
            <li>Add support for more languages</li>
        </ul>
        <p><strong>GitHub:</strong> github.com/movierecommender</p>
    `;
    movieRecommender.showModal('Contact & Contributing', content);
}

function closeModal() {
    movieRecommender.closeModal();
}

/**
 * Initialize the application when DOM is loaded
 */
document.addEventListener('DOMContentLoaded', () => {
    window.movieRecommender = new MovieRecommender();
    console.log('🎬 Indian Movie Recommender initialized successfully!');
});

/**
 * Service Worker registration for PWA functionality (optional)
 */
if ('serviceWorker' in navigator) {
    window.addEventListener('load', () => {
        navigator.serviceWorker.register('/sw.js')
            .then(registration => {
                console.log('SW registered: ', registration);
            })
            .catch(registrationError => {
                console.log('SW registration failed: ', registrationError);
            });
    });
}
