// TMDB API Configuration
const TMDB_IMAGE_BASE = 'https://image.tmdb.org/t/p/w500';
const TMDB_IMAGE_BASE_ORIGINAL = 'https://image.tmdb.org/t/p/original';
const PLACEHOLDER_IMAGE = 'https://via.placeholder.com/500x750?text=No+Poster';

// DOM Elements
const searchInput = document.getElementById('search-input');
const searchResults = document.getElementById('search-results');
const trendingSection = document.getElementById('trending-movies');
const popularSection = document.getElementById('popular-movies');
const topRatedSection = document.getElementById('top-rated-movies');

let searchTimeout;

// Initialize the application
document.addEventListener('DOMContentLoaded', async () => {
    try {
        // Load featured movie for hero section
        await loadFeaturedMovie();
        
        // Load all movie sections in parallel
        await Promise.all([
            loadTrendingMovies(),
            loadPopularMovies(),
            loadTopRatedMovies()
        ]);
        
        // Initialize event listeners
        initEventListeners();
    } catch (error) {
        console.error('Error initializing app:', error);
    }

    // Initialize event listeners
    function initEventListeners() {
        // Search functionality
        if (searchInput) {
            searchInput.addEventListener('input', debounce(handleSearch, 300));
            searchInput.addEventListener('focus', () => {
                if (searchInput.value.trim() !== '') {
                    searchResults.classList.remove('hidden');
                }
            });
            
            document.addEventListener('click', (e) => {
                if (!searchResults.contains(e.target) && e.target !== searchInput) {
                    searchResults.classList.add('hidden');
                }
            });
        }
        
        // Hero play trailer button
        const playTrailerBtn = document.getElementById('hero-play-trailer');
        if (playTrailerBtn) {
            playTrailerBtn.addEventListener('click', () => {
                const videoUrl = playTrailerBtn.getAttribute('data-trailer-url');
                if (videoUrl) {
                    window.open(videoUrl, '_blank');
                } else {
                    // Fallback to movie details page
                    const movieId = playTrailerBtn.getAttribute('data-movie-id');
                    if (movieId) {
                        window.location.href = `/movie/${movieId}`;
                    }
                }
            });
        }
        
        // Smooth scrolling for anchor links
        document.querySelectorAll('a[href^="#"]').forEach(anchor => {
            anchor.addEventListener('click', function (e) {
                e.preventDefault();
                const targetId = this.getAttribute('href');
                if (targetId === '#') return;
                
                const targetElement = document.querySelector(targetId);
                if (targetElement) {
                    window.scrollTo({
                        top: targetElement.offsetTop - 80, // Adjust for fixed header
                        behavior: 'smooth'
                    });
                }
            });
        });
    }

    // Load featured movie for hero section
    async function loadFeaturedMovie() {
        try {
            const response = await fetch('/api/trending?media_type=movie&time_window=day');
            const data = await response.json();
            
            if (data.results && data.results.length > 0) {
                const featuredMovie = data.results[0];
                const title = document.getElementById('hero-title');
                const overview = document.getElementById('hero-overview');
                const backdrop = document.getElementById('hero-backdrop');
                const playBtn = document.getElementById('hero-play-trailer');
                
                if (title) title.textContent = featuredMovie.title || featuredMovie.name || 'Featured Movie';
                if (overview) overview.textContent = featuredMovie.overview || 'Discover amazing content';
                
                if (backdrop) {
                    backdrop.style.backgroundImage = `url('${TMDB_IMAGE_BASE_ORIGINAL}${featuredMovie.backdrop_path}')`;
                }
                
                if (playBtn) {
                    playBtn.setAttribute('data-movie-id', featuredMovie.id);
                    // Try to get trailer URL
                    const movieDetails = await fetch(`/api/movie/${featuredMovie.id}`).then(r => r.json());
                    if (movieDetails.videos && movieDetails.videos.results && movieDetails.videos.results.length > 0) {
                        const trailer = movieDetails.videos.results.find(v => 
                            v.type === 'Trailer' && v.site === 'YouTube'
                        );
                        if (trailer) {
                            playBtn.setAttribute('data-trailer-url', `https://www.youtube.com/watch?v=${trailer.key}`);
                        }
                    }
                }
            }
        } catch (error) {
            console.error('Error loading featured movie:', error);
        }
    }
    
    // Load trending movies
    async function loadTrendingMovies() {
        try {
            const response = await fetch('/api/trending?media_type=movie&time_window=day');
            const data = await response.json();
            if (data.results && trendingSection) {
                updateContentGrid('trending-movies', data.results.slice(0, 10));
            }
        } catch (error) {
            console.error('Error loading trending movies:', error);
        }
    }

    // Load popular movies
    async function loadPopularMovies() {
        try {
            const response = await fetch('/api/movies/popular');
            const data = await response.json();
            if (data.results && popularSection) {
                updateContentGrid('popular-movies', data.results.slice(0, 10));
            }
        } catch (error) {
            console.error('Error loading popular movies:', error);
        }
    }

    // Load top rated movies
    async function loadTopRatedMovies() {
        try {
            const response = await fetch('/api/movies/top_rated');
            const data = await response.json();
            if (data.results && topRatedSection) {
                updateContentGrid('top-rated-movies', data.results.slice(0, 10));
            }
        } catch (error) {
            console.error('Error loading top rated movies:', error);
        }
    }

    // Debounce function to limit API calls
    function debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    }

    // Handle search input
    async function handleSearch(e) {
        const query = e.target.value.trim();
        
        if (query === '') {
            searchResults.classList.add('hidden');
            searchResults.innerHTML = '';
            return;
        }
        
        try {
            const response = await fetch(`/api/search?query=${encodeURIComponent(query)}`);
            const data = await response.json();
            
            if (data.results && data.results.length > 0) {
                displaySearchResults(data.results);
            } else {
                searchResults.innerHTML = `
                    <div class="p-4 text-center text-gray-400">
                        No results found for "${query}"
                    </div>
                `;
                searchResults.classList.remove('hidden');
            }
        } catch (error) {
            console.error('Error searching:', error);
            searchResults.innerHTML = `
                <div class="p-4 text-center text-red-400">
                    Error loading results. Please try again.
                </div>
            `;
            searchResults.classList.remove('hidden');
        }
    }

    // Display search results
    function displaySearchResults(results) {
        // Filter to only include movies and TV shows
        const filteredResults = results.filter(function(item) {
            return (item.media_type === 'movie' || item.media_type === 'tv') && 
                   (item.poster_path || item.backdrop_path);
        }).slice(0, 5); // Limit to 5 results
        
        if (filteredResults.length === 0) {
            searchResults.innerHTML = [
                '<div class="p-4 text-center text-gray-400">',
                '    No results found',
                '</div>'
            ].join('');
            searchResults.classList.remove('hidden');
            return;
        }
        
        const resultsHTML = [
            '<div class="divide-y divide-gray-700">',
            filteredResults.map(function(item) {
                const title = item.title || item.name || 'Untitled';
                const mediaType = item.media_type || (item.title ? 'movie' : 'tv');
                const year = (item.release_date || item.first_air_date || '').substring(0, 4);
                const posterPath = item.poster_path 
                    ? TMDB_IMAGE_BASE + 'w92' + item.poster_path 
                    : PLACEHOLDER_IMAGE;
                
                return [
                    '<a href="/' + mediaType + '/' + item.id + '" class="block p-3 hover:bg-gray-700 transition-colors">',
                    '    <div class="flex items-center">',
                    '        <img src="' + posterPath + '" ', 
                    '             alt="' + title.replace(/"/g, '&quot;') + '" ', 
                    '             class="w-12 h-16 object-cover rounded"',
                    '             onerror="this.src=\'' + PLACEHOLDER_IMAGE + '\'">',
                    '        <div class="ml-3">',
                    '            <h4 class="font-medium text-white">' + title + '</h4>',
                    '            <div class="flex items-center text-sm text-gray-400">',
                    '                <span>' + (mediaType === 'movie' ? 'Movie' : 'TV Show') + '</span>',
                    year ? [
                        '<span class="mx-2">•</span>',
                        '<span>' + year + '</span>'
                    ].join('') : '',
                    '            </div>',
                    '        </div>',
                    '    </div>',
                    '</a>'
                ].join('');
            }).join(''),
            '</div>'
        ].join('');
        
        searchResults.innerHTML = resultsHTML;
        searchResults.classList.remove('hidden');
    }

    // Update content grid with items
    function updateContentGrid(containerId, items) {
        const container = document.getElementById(containerId);
        if (!container) return;
        
        container.innerHTML = items.map(item => createContentCard(item)).join('');
    }

    // Create a content card element
    function createContentCard(item) {
        const title = item.title || item.name || 'Untitled';
        const releaseDate = item.release_date || item.first_air_date;
        const mediaType = item.media_type || (item.title ? 'movie' : 'tv');
        const year = releaseDate ? new Date(releaseDate).getFullYear() : 'N/A';
        const rating = item.vote_average ? Math.round(item.vote_average * 10) / 10 : 'N/A';
        const posterPath = item.poster_path 
            ? `${TMDB_IMAGE_BASE}${item.poster_path}` 
            : PLACEHOLDER_IMAGE;
        const backdropPath = item.backdrop_path 
            ? `${TMDB_IMAGE_BASE_ORIGINAL}${item.backdrop_path}`
            : '';
        
        return `
            <div class="movie-card group">
                <a href="/${mediaType}/${item.id}" class="block h-full">
                    <div class="relative overflow-hidden rounded-t-lg h-4/5">
                        <img src="${posterPath}" 
                             alt="${title}" 
                             onerror="this.src='${PLACEHOLDER_IMAGE}'"
                             class="w-full h-full object-cover transition-transform duration-300 group-hover:scale-105">
                        <div class="absolute inset-0 bg-gradient-to-t from-black to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300 flex items-end p-4">
                            <div class="w-full">
                                <div class="flex justify-between items-center mb-2">
                                    <span class="bg-red-600 text-white text-xs px-2 py-1 rounded">
                                        ${mediaType === 'movie' ? 'MOVIE' : 'TV SHOW'}
                                    </span>
                                    <span class="bg-black bg-opacity-70 text-white text-xs px-2 py-1 rounded flex items-center">
                                        <i class="fas fa-star text-yellow-400 mr-1"></i> ${rating}
                                    </span>
                                </div>
                                <button type="button" class="w-full bg-red-600 hover:bg-red-700 text-white py-2 rounded text-sm font-medium transition-colors">
                                    View Details
                                </button>
                            </div>
                        </div>
                    </div>
                    <div class="p-3 bg-gray-800 h-1/5">
                        <h3 class="font-semibold text-white truncate" title="${title}">${title}</h3>
                        <div class="flex justify-between items-center mt-1 text-sm text-gray-400">
                            <span>${year}</span>
                            <div class="flex items-center">
                                <i class="fas fa-star text-yellow-400 mr-1"></i>
                                <span>${rating}</span>
                            </div>
                        </div>
                    </div>
                </a>
            </div>
        `;
    }

    // Initialize any other components
    initComponents();
});

// Initialize any additional components
function initComponents() {
    // Add any additional component initializations here
    console.log('App initialized');
}

// Helper function to format date
function formatDate(dateString) {
    if (!dateString) return 'N/A';
    const options = { year: 'numeric', month: 'long', day: 'numeric' };
    return new Date(dateString).toLocaleDateString('en-US', options);
}

// Helper function to format duration
function formatDuration(minutes) {
    if (!minutes) return 'N/A';
    const hours = Math.floor(minutes / 60);
    const mins = minutes % 60;
    return `${hours}h ${mins}m`;
}
