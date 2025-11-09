"""
Interactive Movie Recommendation System
Comprehensive backend logic for Indian movie recommendations using TF-IDF and cosine similarity
"""

import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import requests
import re
from typing import List, Dict, Tuple, Optional
import difflib
import json

class MovieRecommendationEngine:
    """
    Main recommendation engine that handles dataset loading, preprocessing,
    similarity computation, and recommendation generation
    """
    
    def __init__(self, dataset_path: str = 'indian_movies_dataset.csv', omdb_api_key: str = None):
        """
        Initialize the recommendation engine
        
        Args:
            dataset_path: Path to the movie dataset CSV file
            omdb_api_key: OMDb API key for fetching movie posters
        """
        self.dataset_path = dataset_path
        self.omdb_api_key = omdb_api_key
        self.df = None
        self.tfidf_matrix = None
        self.cosine_sim = None
        self.vectorizer = None
        self.movie_indices = {}
        
        # Load and prepare the dataset
        self.load_and_prepare_data()
    
    def load_and_prepare_data(self):
        """
        Load the dataset and prepare it for recommendation processing
        Handles missing values and creates combined features for similarity computation
        """
        try:
            # Load the dataset
            self.df = pd.read_csv(self.dataset_path)
            print(f"✅ Loaded {len(self.df)} movies from dataset")
            
            # Handle missing values
            self.df['genres'] = self.df['genres'].fillna('')
            self.df['director'] = self.df['director'].fillna('')
            self.df['main_actors'] = self.df['main_actors'].fillna('')
            self.df['keywords'] = self.df['keywords'].fillna('')
            self.df['language'] = self.df['language'].fillna('Unknown')
            
            # Create combined features for similarity computation
            # This combines all relevant textual features into one string per movie
            self.df['combined_features'] = (
                self.df['genres'] + ' ' +
                self.df['director'] + ' ' +
                self.df['main_actors'] + ' ' +
                self.df['keywords'] + ' ' +
                self.df['language']
            )
            
            # Clean the combined features (remove extra spaces, convert to lowercase)
            self.df['combined_features'] = self.df['combined_features'].str.lower().str.strip()
            
            # Create movie title to index mapping for quick lookup
            self.movie_indices = {title.lower(): idx for idx, title in enumerate(self.df['title'])}
            
            # Compute TF-IDF matrix and cosine similarity
            self.compute_similarity_matrix()
            
            print("✅ Dataset prepared and similarity matrix computed")
            
        except Exception as e:
            print(f"❌ Error loading dataset: {str(e)}")
            raise
    
    def compute_similarity_matrix(self):
        """
        Compute TF-IDF vectors and cosine similarity matrix for all movies
        This is the core of the recommendation algorithm
        """
        try:
            # Initialize TF-IDF Vectorizer
            # TF-IDF converts text to numerical vectors based on term frequency and inverse document frequency
            self.vectorizer = TfidfVectorizer(
                stop_words='english',  # Remove common English stop words
                max_features=5000,     # Limit to top 5000 features for performance
                ngram_range=(1, 2),    # Use both single words and bigrams
                min_df=2,              # Ignore terms that appear in less than 2 documents
                max_df=0.8             # Ignore terms that appear in more than 80% of documents
            )
            
            # Fit and transform the combined features to TF-IDF matrix
            self.tfidf_matrix = self.vectorizer.fit_transform(self.df['combined_features'])
            
            # Compute cosine similarity matrix
            # This creates a matrix where each cell [i,j] represents similarity between movie i and movie j
            self.cosine_sim = cosine_similarity(self.tfidf_matrix, self.tfidf_matrix)
            
            print(f"✅ Computed similarity matrix of shape {self.cosine_sim.shape}")
            
        except Exception as e:
            print(f"❌ Error computing similarity matrix: {str(e)}")
            raise
    
    def find_movie_match(self, input_title: str) -> Tuple[Optional[str], Optional[int]]:
        """
        Find the best matching movie title from the dataset
        Handles partial matches and misspellings using fuzzy string matching
        
        Args:
            input_title: User input movie title
            
        Returns:
            Tuple of (matched_title, movie_index) or (None, None) if no match found
        """
        input_title_clean = input_title.lower().strip()
        
        # Direct match
        if input_title_clean in self.movie_indices:
            idx = self.movie_indices[input_title_clean]
            return self.df.iloc[idx]['title'], idx
        
        # Fuzzy matching for partial titles and misspellings
        all_titles = list(self.movie_indices.keys())
        
        # Find close matches using difflib
        close_matches = difflib.get_close_matches(
            input_title_clean, 
            all_titles, 
            n=1, 
            cutoff=0.6  # 60% similarity threshold
        )
        
        if close_matches:
            matched_title = close_matches[0]
            idx = self.movie_indices[matched_title]
            return self.df.iloc[idx]['title'], idx
        
        # Try partial matching
        for title in all_titles:
            if input_title_clean in title or title in input_title_clean:
                idx = self.movie_indices[title]
                return self.df.iloc[idx]['title'], idx
        
        return None, None
    
    def get_movie_recommendations(self, movie_title: str, num_recommendations: int = 10) -> List[Dict]:
        """
        Get movie recommendations based on input movie title
        
        Args:
            movie_title: Input movie title
            num_recommendations: Number of recommendations to return
            
        Returns:
            List of dictionaries containing movie details and recommendation reasons
        """
        # Find matching movie in dataset
        matched_title, movie_idx = self.find_movie_match(movie_title)
        
        if movie_idx is None:
            return []
        
        # Get similarity scores for the input movie with all other movies
        sim_scores = list(enumerate(self.cosine_sim[movie_idx]))
        
        # Sort movies by similarity score (descending order)
        sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
        
        # Get top N similar movies (excluding the input movie itself)
        similar_movies = sim_scores[1:num_recommendations + 1]
        
        recommendations = []
        input_movie = self.df.iloc[movie_idx]
        
        for movie_idx, similarity_score in similar_movies:
            movie = self.df.iloc[movie_idx]
            
            # Generate recommendation explanation
            reason = self.generate_recommendation_reason(input_movie, movie, similarity_score)
            
            # Get movie poster from OMDb API
            poster_url = self.get_movie_poster(movie['title'])
            
            recommendation = {
                'title': movie['title'],
                'language': movie['language'],
                'genres': movie['genres'],
                'director': movie['director'],
                'main_actors': movie['main_actors'],
                'year': movie['year'],
                'rating': movie['rating'],
                'poster_url': poster_url,
                'similarity_score': round(similarity_score, 3),
                'reason': reason
            }
            
            recommendations.append(recommendation)
        
        return recommendations
    
    def generate_recommendation_reason(self, input_movie: pd.Series, recommended_movie: pd.Series, similarity_score: float) -> str:
        """
        Generate a human-readable explanation for why a movie is recommended
        
        Args:
            input_movie: The input movie data
            recommended_movie: The recommended movie data
            similarity_score: Similarity score between the movies
            
        Returns:
            String explanation for the recommendation
        """
        reasons = []
        
        # Check for common genres
        input_genres = set(input_movie['genres'].lower().split(','))
        rec_genres = set(recommended_movie['genres'].lower().split(','))
        common_genres = input_genres.intersection(rec_genres)
        if common_genres:
            reasons.append(f"Similar genres: {', '.join(common_genres)}")
        
        # Check for same director
        if input_movie['director'].lower() == recommended_movie['director'].lower() and input_movie['director']:
            reasons.append(f"Same director: {input_movie['director']}")
        
        # Check for common actors
        input_actors = set(input_movie['main_actors'].lower().split(','))
        rec_actors = set(recommended_movie['main_actors'].lower().split(','))
        common_actors = input_actors.intersection(rec_actors)
        if common_actors:
            reasons.append(f"Common actors: {', '.join(common_actors)}")
        
        # Check for same language
        if input_movie['language'].lower() == recommended_movie['language'].lower():
            reasons.append(f"Same language: {input_movie['language']}")
        
        # If no specific reasons found, use similarity score
        if not reasons:
            if similarity_score > 0.7:
                reasons.append("Highly similar themes and style")
            elif similarity_score > 0.5:
                reasons.append("Similar storytelling and themes")
            else:
                reasons.append("Related content and style")
        
        return " | ".join(reasons)
    
    def get_movie_poster(self, movie_title: str) -> str:
        """
        Fetch movie poster URL from OMDb API
        
        Args:
            movie_title: Movie title to search for
            
        Returns:
            Poster URL or placeholder URL if not found
        """
        if not self.omdb_api_key:
            return "https://via.placeholder.com/300x450/333/fff?text=No+Poster"
        
        try:
            # Make request to OMDb API
            url = f"http://www.omdbapi.com/?t={movie_title}&apikey={self.omdb_api_key}"
            response = requests.get(url, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('Response') == 'True' and data.get('Poster') != 'N/A':
                    return data['Poster']
            
        except Exception as e:
            print(f"Error fetching poster for {movie_title}: {str(e)}")
        
        # Return placeholder if poster not found
        return "https://via.placeholder.com/300x450/333/fff?text=No+Poster"
    
    def get_autocomplete_suggestions(self, partial_title: str, max_suggestions: int = 5) -> List[str]:
        """
        Get autocomplete suggestions for partial movie titles
        
        Args:
            partial_title: Partial movie title entered by user
            max_suggestions: Maximum number of suggestions to return
            
        Returns:
            List of movie title suggestions
        """
        if len(partial_title) < 2:
            return []
        
        partial_title_lower = partial_title.lower()
        suggestions = []
        
        for title in self.df['title']:
            if partial_title_lower in title.lower():
                suggestions.append(title)
                if len(suggestions) >= max_suggestions:
                    break
        
        return suggestions
    
    def get_movies_by_filters(self, language: str = None, genre: str = None, min_rating: float = None) -> List[Dict]:
        """
        Get movies filtered by language, genre, or rating
        
        Args:
            language: Filter by language
            genre: Filter by genre
            min_rating: Minimum rating filter
            
        Returns:
            List of filtered movies
        """
        filtered_df = self.df.copy()
        
        if language:
            filtered_df = filtered_df[filtered_df['language'].str.lower() == language.lower()]
        
        if genre:
            filtered_df = filtered_df[filtered_df['genres'].str.lower().str.contains(genre.lower(), na=False)]
        
        if min_rating:
            filtered_df = filtered_df[pd.to_numeric(filtered_df['rating'], errors='coerce') >= min_rating]
        
        movies = []
        for _, movie in filtered_df.head(20).iterrows():  # Limit to 20 results
            movies.append({
                'title': movie['title'],
                'language': movie['language'],
                'genres': movie['genres'],
                'director': movie['director'],
                'main_actors': movie['main_actors'],
                'year': movie['year'],
                'rating': movie['rating'],
                'poster_url': self.get_movie_poster(movie['title'])
            })
        
        return movies
    
    def get_dataset_stats(self) -> Dict:
        """
        Get statistics about the dataset
        
        Returns:
            Dictionary containing dataset statistics
        """
        if self.df is None:
            return {}
        
        stats = {
            'total_movies': len(self.df),
            'languages': self.df['language'].value_counts().to_dict(),
            'top_directors': self.df['director'].value_counts().head(10).to_dict(),
            'year_range': f"{self.df['year'].min()} - {self.df['year'].max()}",
            'average_rating': round(pd.to_numeric(self.df['rating'], errors='coerce').mean(), 2)
        }
        
        return stats

# Example usage and testing
if __name__ == "__main__":
    # Initialize the recommendation engine
    # Replace 'your_omdb_api_key' with actual OMDb API key
    recommender = MovieRecommendationEngine(
        dataset_path='indian_movies_dataset.csv',
        omdb_api_key='7f7c782e-0051-449b-8636-94d0a0719c05'  # Replace with your key
    )
    
    # Test recommendations
    print("\n🎬 Testing Movie Recommendations")
    print("=" * 50)
    
    test_movies = ["Dangal", "Baahubali", "3 Idiots"]
    
    for movie in test_movies:
        print(f"\n🔍 Recommendations for '{movie}':")
        recommendations = recommender.get_movie_recommendations(movie, 5)
        
        if recommendations:
            for i, rec in enumerate(recommendations, 1):
                print(f"{i}. {rec['title']} ({rec['year']}) - {rec['language']}")
                print(f"   Genres: {rec['genres']}")
                print(f"   Reason: {rec['reason']}")
                print(f"   Similarity: {rec['similarity_score']}")
                print()
        else:
            print(f"   No recommendations found for '{movie}'")
    
    # Test autocomplete
    print("\n🔍 Testing Autocomplete:")
    suggestions = recommender.get_autocomplete_suggestions("Dan", 5)
    print(f"Suggestions for 'Dan': {suggestions}")
    
    # Dataset stats
    print("\n📊 Dataset Statistics:")
    stats = recommender.get_dataset_stats()
    for key, value in stats.items():
        print(f"{key}: {value}")
