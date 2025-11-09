 ModuleNotFoundError: No module named 'google.generativeai'
"""
Flask Web Application for Interactive Movie Recommendation System
Provides REST API endpoints and serves the frontend interface
"""

from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import json
import os
from movie_recommender import MovieRecommendationEngine

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for frontend-backend communication

# Initialize the recommendation engine
# You can set your OMDb API key here or via environment variable
OMDB_API_KEY = os.getenv('OMDB_API_KEY', '7f7c782e-0051-449b-8636-94d0a0719c05')
recommender = MovieRecommendationEngine(
    dataset_path='indian_movies_dataset.csv',
    omdb_api_key=OMDB_API_KEY
)

@app.route('/')
def index():
    """
    Serve the main HTML page
    """
    return render_template('index.html')

@app.route('/api/recommend', methods=['POST'])
def get_recommendations():
    """
    API endpoint to get movie recommendations
    
    Expected JSON payload:
    {
        "movie_title": "Dangal",
        "num_recommendations": 10
    }
    
    Returns:
    {
        "success": true,
        "input_movie": "Dangal",
        "recommendations": [...]
    }
    """
    try:
        data = request.get_json()
        movie_title = data.get('movie_title', '').strip()
        num_recommendations = data.get('num_recommendations', 10)
        
        if not movie_title:
            return jsonify({
                'success': False,
                'error': 'Movie title is required'
            }), 400
        
        # Get recommendations from the engine
        recommendations = recommender.get_movie_recommendations(
            movie_title, 
            num_recommendations
        )
        
        if not recommendations:
            return jsonify({
                'success': False,
                'error': f'No recommendations found for "{movie_title}". Please check the spelling or try another movie.'
            }), 404
        
        return jsonify({
            'success': True,
            'input_movie': movie_title,
            'recommendations': recommendations
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'An error occurred: {str(e)}'
        }), 500

@app.route('/api/autocomplete', methods=['GET'])
def autocomplete():
    """
    API endpoint for autocomplete suggestions
    
    Query parameters:
    - q: partial movie title
    - limit: maximum number of suggestions (default: 5)
    
    Returns:
    {
        "suggestions": ["Movie 1", "Movie 2", ...]
    }
    """
    try:
        query = request.args.get('q', '').strip()
        limit = int(request.args.get('limit', 5))
        
        if len(query) < 2:
            return jsonify({'suggestions': []})
        
        suggestions = recommender.get_autocomplete_suggestions(query, limit)
        
        return jsonify({'suggestions': suggestions})
        
    except Exception as e:
        return jsonify({
            'suggestions': [],
            'error': str(e)
        })

@app.route('/api/filter', methods=['POST'])
def filter_movies():
    """
    API endpoint to filter movies by language, genre, or rating
    
    Expected JSON payload:
    {
        "language": "Hindi",
        "genre": "Action",
        "min_rating": 7.0
    }
    
    Returns:
    {
        "success": true,
        "movies": [...]
    }
    """
    try:
        data = request.get_json()
        language = data.get('language')
        genre = data.get('genre')
        min_rating = data.get('min_rating')
        
        movies = recommender.get_movies_by_filters(
            language=language,
            genre=genre,
            min_rating=min_rating
        )
        
        return jsonify({
            'success': True,
            'movies': movies
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/stats', methods=['GET'])
def get_stats():
    """
    API endpoint to get dataset statistics
    
    Returns:
    {
        "success": true,
        "stats": {...}
    }
    """
    try:
        stats = recommender.get_dataset_stats()
        return jsonify({
            'success': True,
            'stats': stats
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({
        'success': False,
        'error': 'Endpoint not found'
    }), 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    return jsonify({
        'success': False,
        'error': 'Internal server error'
    }), 500

if __name__ == '__main__':
    # Create templates directory if it doesn't exist
    if not os.path.exists('templates'):
        os.makedirs('templates')
    
    # Create static directory if it doesn't exist
    if not os.path.exists('static'):
        os.makedirs('static')
        os.makedirs('static/css')
        os.makedirs('static/js')
    
    print("🚀 Starting Movie Recommendation Flask App...")
    print("📊 Dataset loaded with", len(recommender.df), "movies")
    print("🌐 Server will be available at: http://localhost:5000")
    
    # Run the Flask app
    app.run(debug=True, host='0.0.0.0', port=5000)
