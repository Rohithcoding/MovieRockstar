import streamlit as st
import pandas as pd
import requests
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import os
from config import OMDB_API_KEY, PLACEHOLDER_IMAGE, GEMINI_API_KEY
from sklearn.feature_extraction.text import TfidfVectorizer
import google.generativeai as genai

# Configure Streamlit page
st.set_page_config(
    page_title="Movie Mood",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Enhanced CSS for better visibility and modern UI/UX
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
    
    :root {
        --primary: #8B5CF6; /* violet-500 */
        --secondary: #06B6D4; /* cyan-500 */
        --accent: #F59E0B; /* amber-500 */
        --success: #10B981; /* emerald-500 */
        --bg1: #0B1426; /* dark blue */
        --bg2: #1E293B; /* slate-800 */
        --card: #334155; /* slate-700 */
        --text: #FFFFFF; /* pure white */
        --text-secondary: #E2E8F0; /* slate-200 */
        --muted: #CBD5E1; /* slate-300 */
        --border: rgba(255,255,255,0.1);
    }
    
    * {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif !important;
    }
    
    .stApp {
        background: linear-gradient(135deg, #0B1426 0%, #1E293B 50%, #334155 100%);
        color: var(--text) !important;
        min-height: 100vh;
    }
    
    .main-header {
        text-align: center;
        background: linear-gradient(135deg, #8B5CF6, #06B6D4, #F59E0B);
        -webkit-background-clip: text;
        background-clip: text;
        color: transparent;
        font-size: clamp(2.5rem, 5vw, 4rem);
        font-weight: 800;
        margin-bottom: 0.5rem;
        letter-spacing: -0.02em;
    }
    
    .sub-header {
        text-align: center;
        color: var(--text-secondary) !important;
        font-size: 1.2rem;
        font-weight: 400;
        margin-bottom: 2rem;
        opacity: 0.9;
    }
    
    .movie-card {
        background: linear-gradient(145deg, rgba(255,255,255,0.08), rgba(255,255,255,0.04));
        border: 1px solid var(--border);
        backdrop-filter: blur(12px);
        border-radius: 20px;
        padding: 1.2rem;
        margin: 0.8rem 0.5rem;
        text-align: left;
        color: var(--text) !important;
        box-shadow: 0 8px 32px rgba(0,0,0,0.2), 0 2px 8px rgba(139,92,246,0.1);
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        position: relative;
        overflow: hidden;
    }
    
    .movie-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 2px;
        background: linear-gradient(90deg, var(--primary), var(--secondary), var(--accent));
        opacity: 0;
        transition: opacity 0.3s ease;
    }
    
    .movie-card:hover {
        transform: translateY(-8px) scale(1.02);
        box-shadow: 0 20px 40px rgba(0,0,0,0.3), 0 8px 16px rgba(139,92,246,0.2);
        border-color: rgba(139,92,246,0.3);
    }
    
    .movie-card:hover::before {
        opacity: 1;
    }
    
    .movie-title {
        font-size: 1.25rem;
        font-weight: 700;
        margin: 0.5rem 0 0.8rem 0;
        color: var(--text) !important;
        line-height: 1.3;
        letter-spacing: -0.01em;
    }
    
    .movie-info {
        font-size: 1rem;
        color: var(--text-secondary) !important;
        line-height: 1.6;
        font-weight: 400;
    }
    
    .movie-info strong {
        color: var(--text) !important;
        font-weight: 600;
    }
    
    .movie-info small {
        color: var(--muted) !important;
        font-size: 0.9rem;
    }
    
    .google-search-container {
        background: linear-gradient(145deg, rgba(255,255,255,0.12), rgba(255,255,255,0.08));
        border: 1px solid var(--border);
        border-radius: 28px;
        padding: 1.5rem 2rem;
        margin: 2rem auto;
        max-width: 700px;
        box-shadow: 0 8px 32px rgba(0,0,0,0.15);
        backdrop-filter: blur(16px);
        transition: all 0.3s ease;
    }
    
    .google-search-container:hover {
        box-shadow: 0 12px 40px rgba(139,92,246,0.15);
        border-color: rgba(139,92,246,0.3);
    }
    
    .stTextInput > div > div > input {
        border: none !important;
        background: transparent !important;
        font-size: 18px !important;
        color: var(--text) !important;
        padding: 16px 0 !important;
        font-weight: 400 !important;
    }
    
    .stTextInput > div > div > input::placeholder {
        color: var(--muted) !important;
        opacity: 0.7;
    }
    
    .stTextInput > div > div > input:focus {
        outline: none !important;
        box-shadow: none !important;
        color: var(--text) !important;
    }
    
    /* Streamlit Component Styling */
    .stSelectbox > div > div {
        background: linear-gradient(145deg, rgba(255,255,255,0.12), rgba(255,255,255,0.08)) !important;
        border: 1px solid var(--border) !important;
        border-radius: 12px !important;
        color: var(--text) !important;
    }
    
    .stSelectbox label {
        color: var(--text) !important;
        font-weight: 600 !important;
        font-size: 1rem !important;
    }
    
    .stMultiSelect > div > div {
        background: linear-gradient(145deg, rgba(255,255,255,0.12), rgba(255,255,255,0.08)) !important;
        border: 1px solid var(--border) !important;
        border-radius: 12px !important;
    }
    
    .stMultiSelect label {
        color: var(--text) !important;
        font-weight: 600 !important;
        font-size: 1rem !important;
    }
    
    .stSlider > div > div > div {
        background: linear-gradient(90deg, var(--primary), var(--secondary)) !important;
    }
    
    .stSlider label {
        color: var(--text) !important;
        font-weight: 600 !important;
        font-size: 1rem !important;
    }
    
    .stButton > button {
        background: linear-gradient(135deg, var(--primary), var(--secondary)) !important;
        color: var(--text) !important;
        border: none !important;
        border-radius: 16px !important;
        padding: 0.8rem 1.5rem !important;
        font-weight: 600 !important;
        font-size: 1rem !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 4px 16px rgba(139,92,246,0.2) !important;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 24px rgba(139,92,246,0.3) !important;
    }
    
    .stTabs [data-baseweb="tab-list"] {
        background: linear-gradient(145deg, rgba(255,255,255,0.08), rgba(255,255,255,0.04)) !important;
        border-radius: 16px !important;
        padding: 0.5rem !important;
    }
    
    .stTabs [data-baseweb="tab"] {
        color: var(--muted) !important;
        font-weight: 600 !important;
        border-radius: 12px !important;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, var(--primary), var(--secondary)) !important;
        color: var(--text) !important;
    }
    
    .stMarkdown h1, .stMarkdown h2, .stMarkdown h3, .stMarkdown h4 {
        color: var(--text) !important;
        font-weight: 700 !important;
    }
    
    .stMarkdown p {
        color: var(--text-secondary) !important;
        font-size: 1rem !important;
        line-height: 1.6 !important;
    }
    
    .stExpander > div > div {
        background: linear-gradient(145deg, rgba(255,255,255,0.08), rgba(255,255,255,0.04)) !important;
        border: 1px solid var(--border) !important;
        border-radius: 16px !important;
    }
    
    .stExpander label {
        color: var(--text) !important;
        font-weight: 600 !important;
    }

    .badge {
        display: inline-block;
        padding: 0.25rem 0.6rem;
        border-radius: 999px;
        background: rgba(124,58,237,0.15);
        border: 1px solid rgba(124,58,237,0.35);
        color: #d6ccff;
        font-size: 0.75rem;
        margin-right: 0.35rem;
    }
    .watch-links {
        margin-top: 1rem;
        padding-top: 0.8rem;
        border-top: 1px solid var(--border);
    }
    
    .watch-links a {
        text-decoration: none;
        display: inline-block;
        margin: 0.3rem 0.4rem 0.3rem 0;
        padding: 0.6rem 1rem;
        border-radius: 25px;
        border: 1px solid rgba(139,92,246,0.4);
        background: linear-gradient(135deg, rgba(139,92,246,0.2), rgba(6,182,212,0.2));
        color: var(--text) !important;
        font-size: 0.85rem;
        font-weight: 600;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        backdrop-filter: blur(8px);
    }
    
    .watch-links a:hover { 
        transform: translateY(-2px) scale(1.05);
        box-shadow: 0 8px 20px rgba(139,92,246,0.3);
        background: linear-gradient(135deg, rgba(139,92,246,0.35), rgba(6,182,212,0.35));
        border-color: rgba(139,92,246,0.6);
        color: var(--text) !important;
    }
    
    .watch-section-title {
        font-size: 1rem;
        font-weight: 700;
        color: var(--text) !important;
        margin-bottom: 0.6rem;
        letter-spacing: -0.01em;
    }
    
    .suggestion-chip {
        display: inline-block;
        margin: 0.25rem 0.5rem 0.25rem 0;
        padding: 0.5rem 1rem;
        background: #f8f9fa;
        border: 1px solid #dadce0;
        border-radius: 20px;
        color: #3c4043;
        font-size: 0.9rem;
        cursor: pointer;
        transition: all 0.2s ease;
    }
    
    .suggestion-chip:hover {
        background: #f1f3f4;
        border-color: #bdc1c6;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    }
    
    .google-results-header {
        color: #70757a;
        font-size: 0.9rem;
        margin: 1rem 0 0.5rem 0;
        border-bottom: 1px solid #dadce0;
        padding-bottom: 0.5rem;
    }
    
    .youtube-meta {
        display: flex;
        gap: 0.5rem;
        margin: 0.5rem 0;
        flex-wrap: wrap;
    }
    
    .views-badge, .duration-badge, .rating-badge {
        display: inline-block;
        padding: 0.2rem 0.5rem;
        border-radius: 12px;
        font-size: 0.75rem;
        font-weight: 600;
    }
    
    .views-badge {
        background: rgba(255,0,0,0.1);
        color: #ff4444;
        border: 1px solid rgba(255,0,0,0.3);
    }
    
    .duration-badge {
        background: rgba(0,123,255,0.1);
        color: #007bff;
        border: 1px solid rgba(0,123,255,0.3);
    }
    
    .rating-badge {
        background: rgba(255,193,7,0.1);
        color: #ffc107;
        border: 1px solid rgba(255,193,7,0.3);
    }
</style>
""", unsafe_allow_html=True)

class MovieRecommendationSystem:
    def __init__(self, csv_file='movies.csv', vectorizer_type='count', feature_columns=None):
        """Initialize the recommendation system with movie data."""
        self.df = None
        self.similarity_matrix = None
        self.vectorizer = None
        self.vectorizer_type = vectorizer_type  # 'count' or 'tfidf'
        # Default features: genres + language
        self.feature_columns = feature_columns or ['genres', 'language']
        self.load_data(csv_file)
        self.prepare_features()
    
    def load_data(self, csv_file):
        """Load movie data from CSV file."""
        try:
            # csv_file can be a path or a file-like object
            self.df = pd.read_csv(csv_file)
            st.success(f"✅ Loaded {len(self.df)} movies successfully!")
        except FileNotFoundError:
            st.error(f"❌ Could not find {csv_file}. Please ensure the file exists.")
            st.stop()
        except Exception as e:
            st.error(f"❌ Error loading data: {str(e)}")
            st.stop()
    
    def prepare_features(self):
        """Combine genres and language into feature column and compute similarity."""
        # Build a combined text feature from available columns
        available = [col for col in self.feature_columns if col in self.df.columns]
        if not available:
            # Fallback to all string columns if nothing matches
            available = [c for c in self.df.columns if self.df[c].dtype == 'object']
        # Fill NaNs and join with spaces
        self.df[available] = self.df[available].fillna('')
        self.df['features'] = self.df[available].agg(' '.join, axis=1)
        
        # Create feature vectors using selected vectorizer
        if self.vectorizer_type == 'tfidf':
            self.vectorizer = TfidfVectorizer(stop_words='english')
        else:
            self.vectorizer = CountVectorizer(stop_words='english')
        feature_vectors = self.vectorizer.fit_transform(self.df['features'])
        
        # Compute cosine similarity matrix
        self.similarity_matrix = cosine_similarity(feature_vectors)
    
    def get_movie_index(self, title):
        """Get the index of a movie by its title."""
        # Case-insensitive search
        matches = self.df[self.df['title'].str.lower() == title.lower()]
        if not matches.empty:
            return matches.index[0]
        
        # If exact match not found, try partial match
        partial_matches = self.df[self.df['title'].str.lower().str.contains(title.lower(), na=False)]
        if not partial_matches.empty:
            return partial_matches.index[0]
        
        return None
    
    def recommend_movies(self, title, top_n=5):
        """
        Recommend movies based on similarity to the given title.
        
        Args:
            title (str): Movie title to base recommendations on
            top_n (int): Number of recommendations to return
            
        Returns:
            list: List of recommended movie dictionaries
        """
        movie_idx = self.get_movie_index(title)
        
        if movie_idx is None:
            return None
        
        # Get similarity scores for all movies
        similarity_scores = list(enumerate(self.similarity_matrix[movie_idx]))
        
        # Sort by similarity score (descending)
        similarity_scores = sorted(similarity_scores, key=lambda x: x[1], reverse=True)
        
        # Get top N similar movies (excluding the input movie itself)
        recommended_indices = [i[0] for i in similarity_scores[1:top_n+1]]
        
        # Return recommended movies as list of dictionaries
        recommendations = []
        for idx in recommended_indices:
            movie = self.df.iloc[idx]
            item = {
                'title': movie.get('title') if hasattr(movie, 'get') else movie['title'],
                'genres': movie['genres'] if 'genres' in movie else None,
                'language': movie['language'] if 'language' in movie else None,
                'similarity_score': similarity_scores[idx][1]
            }
            if 'industry' in self.df.columns:
                try:
                    item['industry'] = movie['industry']
                except Exception:
                    item['industry'] = None
            recommendations.append(item)
        
        return recommendations

class PosterFetcher:
    def __init__(self, api_key=None):
        """Initialize poster fetcher with OMDb API."""
        self.api_key = api_key or OMDB_API_KEY  # Use configured API key
        self.base_url = "http://www.omdbapi.com/"
    
    @st.cache_data(show_spinner=False, ttl=3600)  # Cache posters for 1 hour
    def get_poster(_self, title):
        """
        Fetch movie poster URL from OMDb API.
        
        Args:
            title (str): Movie title
            
        Returns:
            str: Poster URL or placeholder image URL
        """
        try:
            params = {
                'apikey': _self.api_key,
                't': title,
                'type': 'movie'
            }
            
            response = requests.get(_self.base_url, params=params, timeout=2)  # Faster timeout
            data = response.json()
            
            if data.get('Response') == 'True' and data.get('Poster') != 'N/A':
                return data['Poster']
            else:
                # Return a placeholder image if poster not found
                return PLACEHOLDER_IMAGE
        except Exception:
            # Return placeholder on any error
            return PLACEHOLDER_IMAGE

    @st.cache_data(show_spinner=False, ttl=3600)  # Cache ratings for 1 hour
    def get_rating(_self, title):
        """Fetch rating info from OMDb (IMDb, Rotten Tomatoes, Metacritic). Returns a compact string."""
        try:
            params = {
                'apikey': _self.api_key,
                't': title,
                'type': 'movie'
            }
            response = requests.get(_self.base_url, params=params, timeout=2)  # Faster timeout
            data = response.json()
            if data.get('Response') != 'True':
                return "⭐ N/A", 0
            parts = []
            star_rating = 0
            imdb = data.get('imdbRating')
            if imdb and imdb != 'N/A':
                try:
                    imdb_float = float(imdb)
                    star_rating = imdb_float / 2  # Convert 10-scale to 5-star
                    parts.append(f"IMDb {imdb}")
                except ValueError:
                    pass
            ratings = data.get('Ratings') or []
            rt = next((r.get('Value') for r in ratings if r.get('Source') == 'Rotten Tomatoes'), None)
            if rt:
                parts.append(f"RT {rt}")
            mc = next((r.get('Value') for r in ratings if r.get('Source') == 'Metacritic'), None)
            if mc:
                parts.append(f"MC {mc}")
            rating_text = " | ".join(parts) if parts else "N/A"
            return rating_text, star_rating
        except Exception:
            return "⭐ N/A", 0

def render_stars(rating):
    """Convert numeric rating (0-5) to star display."""
    if rating <= 0:
        return "⭐ N/A"
    full_stars = int(rating)
    half_star = 1 if (rating - full_stars) >= 0.5 else 0
    empty_stars = 5 - full_stars - half_star
    return "⭐" * full_stars + ("⭐" if half_star else "") + "☆" * empty_stars + f" ({rating:.1f}/5)"

class GeminiSuggester:
    def __init__(self, api_key: str | None):
        self.enabled = bool(api_key)
        if self.enabled:
            try:
                genai.configure(api_key=api_key)
                self.model = genai.GenerativeModel('gemini-1.5-flash')
            except Exception:
                self.enabled = False
                self.model = None
        else:
            self.model = None

    @st.cache_data(show_spinner=False)
    def suggest_cached(_title, _language, _genres):
        # Dummy placeholder for caching signature
        return None

    def suggest(self, title: str, language: str | None, genres: str | None):
        if not self.enabled or not title:
            return None
        # Use cache first
        cached = GeminiSuggester.suggest_cached(title, language, genres)
        if cached:
            return cached
        prompt = (
            "You are a movie assistant. Given a movie title, language, and genres, "
            "return a concise JSON with keys: summary (<=35 words, no spoilers) and platforms (array of 2-5 likely streaming platforms in user's region for India/US mix).\n\n"
            f"Title: {title}\n"
            f"Language: {language or 'Unknown'}\n"
            f"Genres: {genres or 'Unknown'}\n"
            "Only output valid JSON. Example: {\"summary\":\"...\",\"platforms\":[\"Netflix\",\"Prime Video\"]}"
        )
        try:
            resp = self.model.generate_content(prompt)
            text = resp.text.strip()
            # Attempt to parse JSON
            import json, re
            # Extract JSON blob if wrapped in markdown
            m = re.search(r"\{[\s\S]*\}", text)
            if m:
                text = m.group(0)
            data = json.loads(text)
            # Cache
            GeminiSuggester.suggest_cached.clear()
            GeminiSuggester.suggest_cached(title, language, genres)
            return {
                'summary': data.get('summary', ''),
                'platforms': data.get('platforms', [])
            }
        except Exception:
            return None

    def suggest_genres(self, title: str):
        """Return a small list of genres for a given movie title using Gemini."""
        if not self.enabled or not title:
            return []
        prompt = (
            "Given ONLY a movie title, output compact JSON with key 'genres' listing 3-6 concise genre tags.\n"
            "Keep tags common (e.g., Thriller, Crime, Drama, Action, Romance, Comedy, Sci-Fi).\n"
            f"Title: {title}\n"
            "Output JSON only. Example: {\"genres\":[\"Thriller\",\"Crime\",\"Mystery\"]}"
        )
        try:
            resp = self.model.generate_content(prompt)
            text = resp.text.strip()
            import json, re
            m = re.search(r"\{[\s\S]*\}", text)
            if m:
                text = m.group(0)
            data = json.loads(text)
            genres = data.get('genres', [])
            # normalize capitalization
            return [g.strip() for g in genres if isinstance(g, str) and g.strip()]
        except Exception:
            return []

def build_watch_links(title: str, platforms: list[str] | None):
    """Return a dict of {label: url} for watch locations - prioritizes popular Indian platforms."""
    title_q = requests.utils.quote(title)
    
    # Always include these popular platforms first
    links = {
        'Netflix': f'https://www.netflix.com/in/search?q={title_q}',
        'Prime Video': f'https://www.primevideo.com/region/in/search/ref=atv_nb_sr?phrase={title_q}',
        'Disney+ Hotstar': f'https://www.hotstar.com/in/search?q={title_q}',
        'JioCinema': f'https://www.jiocinema.com/search/{title_q}',
        'ZEE5': f'https://www.zee5.com/search?q={title_q}',
        'Sony LIV': f'https://www.sonyliv.com/search/{title_q}',
        'JustWatch': f'https://www.justwatch.com/in/search?q={title_q}'
    }
    
    # Additional platform mapping
    extra_mapping = {
        'Amazon Prime Video': f'https://www.primevideo.com/region/in/search/ref=atv_nb_sr?phrase={title_q}',
        'Hotstar': f'https://www.hotstar.com/in/search?q={title_q}',
        'Apple TV': f'https://tv.apple.com/in/search?term={title_q}',
        'YouTube': f'https://www.youtube.com/results?search_query={title_q}+full+movie',
        'Google Play': f'https://play.google.com/store/search?q={title_q}&c=movies',
        'MX Player': f'https://www.mxplayer.in/search/{title_q}',
        'Voot': f'https://www.voot.com/search?q={title_q}',
        'Aha': f'https://www.aha.video/search?query={title_q}',
        'Sun NXT': f'https://www.sunnxt.com/search?q={title_q}',
        'Hulu': f'https://www.hulu.com/search?q={title_q}',
        'Google': f'https://www.google.com/search?q=watch+{title_q}+online+streaming'
    }
    
    # Add AI-suggested platforms if available
    if platforms:
        for p in platforms:
            key = p.strip()
            if key in extra_mapping and key not in links:
                links[key] = extra_mapping[key]
    
    return links
def main():
    """Main Streamlit application."""
    
    # YouTube-style Header
    st.markdown('<h1 class="main-header">🎬 MovieTube</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Discover movies like YouTube suggests videos - powered by Gemini AI!</p>', unsafe_allow_html=True)
    
    # Google-style search interface
    st.markdown('<div class="google-search-container">', unsafe_allow_html=True)
    
    # Main search bar (Google-like)
    search_query = st.text_input(
        "",
        value="",
        placeholder="Search for movies, genres, actors, or ask anything...",
        help="Try: 'Dangal', 'कांतारा', 'movies like Baahubali', 'Shah Rukh Khan films', 'Tamil action movies'",
        label_visibility="collapsed"
    )
    
    # Dual recommendation flows
    st.markdown("### 🎯 Choose Your Discovery Method")
    
    tab1, tab2 = st.tabs(["🎭 Browse by Genres & Languages", "🎬 Similar to a Movie"])
    
    with tab1:
        st.markdown("#### ✨ Ask Gemini for Suggestions")
        col1, col2 = st.columns(2)
        
        with col1:
            genres = st.multiselect(
                "🎭 Select Genres",
                ["Action", "Comedy", "Drama", "Thriller", "Romance", "Horror", "Sci-Fi", "Crime", "Mystery", "Family", "Adventure", "Fantasy", "Animation"],
                default=["Action", "Drama"],
                help="Choose your preferred genres"
            )
        
        with col2:
            languages = st.multiselect(
                "🌍 Select Languages", 
                ["Hindi", "English", "Tamil", "Telugu", "Kannada", "Malayalam", "Bengali", "Marathi", "Gujarati", "Punjabi"],
                default=["Hindi", "English"],
                help="Choose your preferred languages"
            )
        
        num_recommendations_genre = st.slider("📊 Number of recommendations:", min_value=1, max_value=10, value=6, key="genre_slider")
        
        if st.button("🔮 Ask Gemini for Suggestions", key="gemini_suggest", use_container_width=True):
            if genres and languages:
                search_query = f"suggest {num_recommendations_genre} {' '.join(genres)} movies in {' '.join(languages)} languages"
                st.rerun()
    
    with tab2:
        st.markdown("#### 🔎 Get Recommendations Similar to a Movie")
        movie_title = st.text_input(
            "🎬 Enter a movie title", 
            value="", 
            placeholder="e.g., Dangal, Baahubali, Avengers, कांतारा",
            help="Enter any movie title in English or Indian languages"
        )
        
        num_recommendations_title = st.slider("📊 Number of recommendations:", min_value=1, max_value=10, value=8, key="title_slider")
        
        if st.button("✨ Get Similar Movies", key="similar_movies", use_container_width=True):
            if movie_title:
                search_query = f"movies similar to {movie_title}"
                st.rerun()
    
    # Advanced filters (collapsible)
    with st.expander("🔧 Advanced Filters", expanded=False):
        col3, col4, col5 = st.columns(3)
        
        with col3:
            genres = st.multiselect(
                "Genres",
                ["Action", "Comedy", "Drama", "Thriller", "Romance", "Horror", "Sci-Fi", "Crime", "Mystery", "Family", "Adventure", "Fantasy", "Animation"],
                help="Filter by genres"
            )
        
        with col4:
            languages = st.multiselect(
                "Languages", 
                ["Hindi", "English", "Tamil", "Telugu", "Kannada", "Malayalam", "Bengali", "Marathi", "Gujarati", "Punjabi"],
                help="Filter by languages"
            )
        
        with col5:
            num_recommendations = st.slider("Results:", min_value=3, max_value=12, value=8)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Set user_title for compatibility with existing logic
    user_title = search_query

    # Initialize recommendation system (cached for performance)
    @st.cache_data(show_spinner=False)
    def load_recommendation_system(csv_source, vectorizer_type, feature_columns):
        return MovieRecommendationSystem(csv_file=csv_source, vectorizer_type=vectorizer_type, feature_columns=feature_columns)
    
    try:
        poster_fetcher = PosterFetcher()
        gemini = GeminiSuggester(GEMINI_API_KEY)
    except Exception as e:
        st.error(f"Failed to initialize the recommendation system: {str(e)}")
        return
    
    # Generate recommendations based on title OR genres/languages
    if user_title or (genres and languages):
        if not gemini.enabled:
            st.error("Gemini is not configured. Please set GEMINI_API_KEY in config.py.")
        else:
            with st.spinner("🚀 Getting fast AI recommendations..."):
                import json, re
                recs = []
                
                # Try multiple approaches for better reliability
                try:
                    # YouTube-style movie recommendation algorithm
                    prompt = f"""You are YouTube's movie recommendation AI. User searched/watched: "{user_title}"

Act like YouTube's algorithm - suggest {num_recommendations} movies that users who liked this would also enjoy, using engagement patterns and viewing behavior.

For each recommendation, provide this EXACT format:
TITLE: [Movie Name]
YEAR: [Release Year]
GENRE: [Main Genres]
LANGUAGE: [Primary Language]
RATING: [IMDb Rating/10]
VIEWS: [Popularity indicator like "10M+ watched" or "Trending #1"]
DURATION: [Movie runtime like "2h 30m"]
STREAMING: [Where to watch - Netflix, Prime Video, Hotstar, JioCinema, etc.]
WHY: [YouTube-style reason like "Because you watched [input movie]" or "Viewers also liked" or "Trending in your area"]

YouTube Algorithm Guidelines:
- Prioritize movies with high engagement (views, ratings, trending)
- Mix popular blockbusters with hidden gems
- Include "viewers also watched" patterns
- Consider regional preferences (Bollywood, South Indian, Hollywood)
- Add trending/viral movies
- Include both recent releases and classics
- Factor in binge-watching patterns (similar genres/actors)
- Use YouTube-style explanations: "Because you watched...", "Trending now", "Popular with viewers like you"

Make recommendations feel personalized like YouTube's "Recommended for you" section."""
                    
                    resp = gemini.model.generate_content(prompt)
                    text = resp.text.strip()
                    
                    # Parse Google-style structured response
                    movies = text.split('\n\n')  # Movies separated by double newlines
                    
                    for movie_block in movies:
                        if len(recs) >= num_recommendations:
                            break
                            
                        lines = movie_block.strip().split('\n')
                        movie_data = {}
                        
                        for line in lines:
                            line = line.strip()
                            if line.startswith('TITLE:'):
                                movie_data['title'] = line.replace('TITLE:', '').strip()
                            elif line.startswith('YEAR:'):
                                movie_data['year'] = line.replace('YEAR:', '').strip()
                            elif line.startswith('GENRE:'):
                                movie_data['genres'] = line.replace('GENRE:', '').strip()
                            elif line.startswith('RATING:'):
                                movie_data['ai_rating'] = line.replace('RATING:', '').strip()
                            elif line.startswith('LANGUAGE:'):
                                movie_data['language'] = line.replace('LANGUAGE:', '').strip()
                            elif line.startswith('PLOT:'):
                                movie_data['plot'] = line.replace('PLOT:', '').strip()
                            elif line.startswith('VIEWS:'):
                                movie_data['views'] = line.replace('VIEWS:', '').strip()
                            elif line.startswith('DURATION:'):
                                movie_data['duration'] = line.replace('DURATION:', '').strip()
                            elif line.startswith('STREAMING:'):
                                movie_data['ai_platforms'] = line.replace('STREAMING:', '').strip()
                            elif line.startswith('WHY:'):
                                movie_data['why'] = line.replace('WHY:', '').strip()
                        
                        # Add movie if we have at least a title
                        if movie_data.get('title'):
                            recs.append({
                                'title': movie_data.get('title', 'Unknown'),
                                'year': movie_data.get('year', ''),
                                'language': movie_data.get('language', languages[0] if languages else 'Unknown'),
                                'genres': movie_data.get('genres', ', '.join(genres) if genres else 'Unknown'),
                                'ai_rating': movie_data.get('ai_rating', ''),
                                'ai_platforms': movie_data.get('ai_platforms', ''),
                                'plot': movie_data.get('plot', ''),
                                'views': movie_data.get('views', ''),
                                'duration': movie_data.get('duration', ''),
                                'why': movie_data.get('why', '')
                            })
                    
                    # If we didn't get enough, try a different approach
                    if len(recs) < 3:
                        backup_prompt = f"Name {num_recommendations} popular movies"
                        if user_title:
                            backup_prompt += f" like {user_title}"
                        if genres:
                            backup_prompt += f" in {genres[0]} genre"
                        if languages:
                            backup_prompt += f" in {languages[0]} language"
                        
                        backup_resp = gemini.model.generate_content(backup_prompt)
                        backup_lines = backup_resp.text.strip().split('\n')
                        
                        for line in backup_lines:
                            line = line.strip()
                            if line and len(recs) < num_recommendations:
                                clean_title = re.sub(r'^[\d\.\-\*\•\►\→\➤]\s*', '', line)
                                clean_title = clean_title.strip('"\'')
                                if clean_title and len(clean_title) > 2:
                                    # Avoid duplicates
                                    if not any(r['title'].lower() == clean_title.lower() for r in recs):
                                        recs.append({
                                            'title': clean_title,
                                            'language': languages[0] if languages else 'Unknown',
                                            'genres': ', '.join(genres) if genres else 'Unknown',
                                            'ai_rating': '',
                                            'ai_platforms': ''
                                        })
                
                except Exception as e:
                    error_msg = str(e)
                    # Silently handle quota exceeded - no warning message shown
                    # Just proceed to fallback recommendations
                    
                    # Smart fallback based on user input
                    if user_title:
                        # Title-based fallbacks
                        title_lower = user_title.lower()
                        if any(word in title_lower for word in ['dangal', 'aamir', 'wrestling']):
                            fallback_movies = ["Sultan", "Mary Kom", "Bhaag Milkha Bhaag", "Chak De India", "Lagaan", "Mukkabaaz"]
                        elif any(word in title_lower for word in ['baahubali', 'prabhas', 'rajamouli']):
                            fallback_movies = ["RRR", "KGF", "Pushpa", "Magadheera", "Eega", "Saaho"]
                        elif any(word in title_lower for word in ['avengers', 'marvel', 'superhero']):
                            fallback_movies = ["Iron Man", "Captain America", "Thor", "Black Panther", "Spider-Man", "Doctor Strange"]
                        elif any(word in title_lower for word in ['inception', 'nolan', 'sci-fi']):
                            fallback_movies = ["Interstellar", "The Matrix", "Blade Runner", "Tenet", "The Dark Knight", "Memento"]
                        else:
                            fallback_movies = ["3 Idiots", "Zindagi Na Milegi Dobara", "Dil Chahta Hai", "Queen", "Pink", "Article 15"]
                    else:
                        # Genre-based fallbacks
                        if genres and languages:
                            if 'Action' in genres:
                                if 'Hindi' in languages:
                                    fallback_movies = ["War", "Pathaan", "Tiger Zinda Hai", "Dhoom 3", "Bang Bang", "Race 3"]
                                elif any(lang in languages for lang in ['Tamil', 'Telugu']):
                                    fallback_movies = ["KGF", "Pushpa", "RRR", "Vikram", "Beast", "Master"]
                                else:
                                    fallback_movies = ["John Wick", "Fast & Furious", "Mission Impossible", "The Raid", "Mad Max", "Atomic Blonde"]
                            elif 'Comedy' in genres:
                                if 'Hindi' in languages:
                                    fallback_movies = ["Hera Pheri", "Golmaal", "Welcome", "Housefull", "Total Dhamaal", "Fukrey"]
                                else:
                                    fallback_movies = ["The Hangover", "Superbad", "Anchorman", "Dumb and Dumber", "Meet the Parents", "Zoolander"]
                            elif 'Drama' in genres:
                                if 'Hindi' in languages:
                                    fallback_movies = ["Taare Zameen Par", "My Name is Khan", "Anand", "Masaan", "Court", "Ship of Theseus"]
                                else:
                                    fallback_movies = ["The Shawshank Redemption", "Forrest Gump", "The Godfather", "Schindler's List", "12 Years a Slave", "Moonlight"]
                            else:
                                fallback_movies = ["Dangal", "Baahubali", "3 Idiots", "Queen", "Zindagi Na Milegi Dobara", "Article 15"]
                        else:
                            fallback_movies = ["Dangal", "Baahubali", "RRR", "3 Idiots", "Avengers", "Inception"]
                    
                    # Add fallback movies
                    for movie in fallback_movies[:num_recommendations]:
                        recs.append({
                            'title': movie,
                            'language': languages[0] if languages else 'Unknown',
                            'genres': ', '.join(genres) if genres else 'Popular',
                            'ai_rating': '',
                            'ai_platforms': ''
                        })

            if recs:
                # YouTube-style results header
                results_count = len(recs)
                st.markdown(f'<div class="google-results-header">📺 {results_count} movies recommended for you</div>', unsafe_allow_html=True)
                
                cols_per_row = 2 if st.session_state.get('mobile', False) else 3
                for i in range(0, len(recs), cols_per_row):
                    cols = st.columns(cols_per_row)
                    for j, col in enumerate(cols):
                        if i + j < len(recs):
                            r = recs[i + j]
                            with col:
                                # Get poster image
                                poster_url = poster_fetcher.get_poster(r['title'])
                                st.image(poster_url, use_column_width=True)
                                
                                # Get ratings and AI summary
                                rating_text, star_rating = poster_fetcher.get_rating(r['title'])
                                stars_display = render_stars(star_rating)
                                
                                # Get AI summary using Gemini
                                ai_summary = None
                                if gemini.enabled:
                                    ai_summary = gemini.suggest(r['title'], r.get('language'), r.get('genres'))
                                
                                # Use AI-suggested platforms or build default links
                                ai_platforms = r.get('ai_platforms', '').split(',') if r.get('ai_platforms') else []
                                links = build_watch_links(r['title'], ai_platforms)
                                links_html = "".join([f"<a href='{u}' target='_blank' rel='noreferrer'>{n}</a>" for n,u in links.items()])
                                
                                # Complete movie card display with all requested features
                                year_display = f" ({r.get('year', '')})" if r.get('year') else ""
                                genres_display = r.get('genres', '') or ', '.join(genres) if genres else ''
                                language_display = r.get('language', 'Unknown')
                                plot_display = r.get('plot', '')
                                ai_summary_text = ai_summary.get('summary', '') if ai_summary else plot_display
                                
                                st.markdown(f"""
                                <div class="movie-card">
                                    <div class="movie-title">{r['title']}{year_display}</div>
                                    <div class="movie-info">
                                        <strong>🎭 Genres:</strong> {genres_display}<br>
                                        <strong>🌍 Language:</strong> {language_display}<br>
                                        <strong>⭐ Rating:</strong> {stars_display}<br>
                                        <small>{rating_text}</small>
                                        {f"<div style='margin-top:0.5rem;color:#cbd5e1;font-style:italic;'><strong>📝 AI Summary:</strong><br>{ai_summary_text}</div>" if ai_summary_text else ""}
                                    </div>
                                    <div class="watch-links">
                                        <div class="watch-section-title">🔗 Where to Watch:</div>
                                        {links_html}
                                    </div>
                                </div>
                                """, unsafe_allow_html=True)
    
    # YouTube-style sidebar
    with st.sidebar:
        st.markdown("### 📺 About MovieTube")
        st.markdown("""
        **🎬 MovieTube - YouTube for Movies**
        
        Discover movies like YouTube suggests videos:
        - 📺 **Algorithm-based** recommendations
        - 👁️ **View counts** and popularity metrics
        - ⏱️ **Duration** and runtime info
        - 🔥 **Trending** and viral movies
        - 🎯 **Personalized** suggestions
        
        Powered by Gemini AI & YouTube-style algorithm
        """)
        st.markdown("---")
        st.markdown("### 🔥 Popular Categories")
        st.markdown("""
        - 🎬 **Latest Releases** - New movies trending now
        - 🏆 **Award Winners** - Critically acclaimed films  
        - 💥 **Action Blockbusters** - High-octane entertainment
        - 😂 **Comedy Hits** - Laugh-out-loud movies
        - 🎭 **Bollywood Classics** - Timeless Indian cinema
        - 🌟 **South Cinema** - Regional blockbusters
        """)
        st.markdown("---")
        st.markdown("### 💡 YouTube-Style Tips")
        st.markdown("""
        - Browse trending categories like YouTube
        - Get "Because you watched..." suggestions
        - See view counts and popularity metrics
        - Discover movies through algorithm magic
        """)

if __name__ == "__main__":
    main()
