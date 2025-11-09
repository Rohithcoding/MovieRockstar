#!/usr/bin/env python3
"""
Test Script for Indian Movie Recommendation System
Tests core functionality and API endpoints
"""

import sys
import os
import requests
import time
from movie_recommender import MovieRecommendationEngine

def test_recommendation_engine():
    """Test the core recommendation engine"""
    print("🧪 Testing Recommendation Engine...")
    print("=" * 50)
    
    try:
        # Initialize the engine
        recommender = MovieRecommendationEngine(
            dataset_path='indian_movies_dataset.csv',
            omdb_api_key='7f7c782e-0051-449b-8636-94d0a0719c05'
        )
        
        print(f"✅ Dataset loaded: {len(recommender.df)} movies")
        
        # Test movie search
        test_movies = ["Dangal", "Baahubali", "3 Idiots", "dangal", "baahu"]
        
        for movie in test_movies:
            print(f"\n🔍 Testing: '{movie}'")
            matched_title, idx = recommender.find_movie_match(movie)
            
            if matched_title:
                print(f"   ✅ Found: {matched_title}")
                
                # Get recommendations
                recommendations = recommender.get_movie_recommendations(movie, 3)
                print(f"   📽️  Got {len(recommendations)} recommendations:")
                
                for i, rec in enumerate(recommendations[:3], 1):
                    print(f"      {i}. {rec['title']} ({rec['year']}) - {rec['similarity_score']}")
            else:
                print(f"   ❌ Not found: {movie}")
        
        # Test autocomplete
        print(f"\n🔍 Testing Autocomplete:")
        suggestions = recommender.get_autocomplete_suggestions("Dan", 5)
        print(f"   Suggestions for 'Dan': {suggestions}")
        
        # Test filters
        print(f"\n🔍 Testing Filters:")
        hindi_movies = recommender.get_movies_by_filters(language="Hindi", min_rating=8.0)
        print(f"   Hindi movies with 8.0+ rating: {len(hindi_movies)}")
        
        # Test stats
        print(f"\n📊 Dataset Statistics:")
        stats = recommender.get_dataset_stats()
        for key, value in stats.items():
            if isinstance(value, dict):
                print(f"   {key}: {len(value)} items")
            else:
                print(f"   {key}: {value}")
        
        print("\n✅ All recommendation engine tests passed!")
        return True
        
    except Exception as e:
        print(f"\n❌ Recommendation engine test failed: {str(e)}")
        return False

def test_flask_api():
    """Test Flask API endpoints"""
    print("\n🌐 Testing Flask API...")
    print("=" * 50)
    
    base_url = "http://localhost:5000"
    
    # Test if server is running
    try:
        response = requests.get(base_url, timeout=5)
        if response.status_code == 200:
            print("✅ Flask server is running")
        else:
            print("❌ Flask server returned error")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Flask server is not running")
        print("   Please start the server with: python app_flask.py")
        return False
    except Exception as e:
        print(f"❌ Error connecting to server: {str(e)}")
        return False
    
    # Test recommendation API
    try:
        print("\n🔍 Testing /api/recommend endpoint...")
        response = requests.post(
            f"{base_url}/api/recommend",
            json={"movie_title": "Dangal", "num_recommendations": 5},
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                recommendations = data.get('recommendations', [])
                print(f"✅ Got {len(recommendations)} recommendations for Dangal")
                
                if recommendations:
                    print("   Sample recommendation:")
                    rec = recommendations[0]
                    print(f"   - {rec['title']} ({rec['year']})")
                    print(f"   - Reason: {rec.get('reason', 'N/A')}")
            else:
                print(f"❌ API returned error: {data.get('error')}")
                return False
        else:
            print(f"❌ API request failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing recommendation API: {str(e)}")
        return False
    
    # Test autocomplete API
    try:
        print("\n🔍 Testing /api/autocomplete endpoint...")
        response = requests.get(
            f"{base_url}/api/autocomplete?q=Dan&limit=3",
            timeout=5
        )
        
        if response.status_code == 200:
            data = response.json()
            suggestions = data.get('suggestions', [])
            print(f"✅ Got {len(suggestions)} autocomplete suggestions")
            print(f"   Suggestions: {suggestions}")
        else:
            print(f"❌ Autocomplete API failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing autocomplete API: {str(e)}")
        return False
    
    # Test filter API
    try:
        print("\n🔍 Testing /api/filter endpoint...")
        response = requests.post(
            f"{base_url}/api/filter",
            json={"language": "Hindi", "min_rating": 8.0},
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                movies = data.get('movies', [])
                print(f"✅ Got {len(movies)} filtered movies")
            else:
                print(f"❌ Filter API returned error: {data.get('error')}")
                return False
        else:
            print(f"❌ Filter API failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing filter API: {str(e)}")
        return False
    
    # Test stats API
    try:
        print("\n🔍 Testing /api/stats endpoint...")
        response = requests.get(f"{base_url}/api/stats", timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                stats = data.get('stats', {})
                print(f"✅ Got dataset stats:")
                print(f"   Total movies: {stats.get('total_movies')}")
                print(f"   Languages: {len(stats.get('languages', {}))}")
                print(f"   Average rating: {stats.get('average_rating')}")
            else:
                print(f"❌ Stats API returned error: {data.get('error')}")
                return False
        else:
            print(f"❌ Stats API failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing stats API: {str(e)}")
        return False
    
    print("\n✅ All Flask API tests passed!")
    return True

def test_file_structure():
    """Test if all required files exist"""
    print("\n📁 Testing File Structure...")
    print("=" * 50)
    
    required_files = [
        'indian_movies_dataset.csv',
        'movie_recommender.py',
        'app_flask.py',
        'requirements_flask.txt',
        'templates/index.html',
        'static/css/style.css',
        'static/js/script.js'
    ]
    
    missing_files = []
    
    for file_path in required_files:
        if os.path.exists(file_path):
            print(f"✅ {file_path}")
        else:
            print(f"❌ {file_path} - MISSING")
            missing_files.append(file_path)
    
    if missing_files:
        print(f"\n❌ Missing {len(missing_files)} required files")
        return False
    else:
        print(f"\n✅ All {len(required_files)} required files found!")
        return True

def main():
    """Run all tests"""
    print("🎬 Indian Movie Recommendation System - Test Suite")
    print("=" * 60)
    
    all_tests_passed = True
    
    # Test file structure
    if not test_file_structure():
        all_tests_passed = False
    
    # Test recommendation engine
    if not test_recommendation_engine():
        all_tests_passed = False
    
    # Test Flask API (only if server is running)
    print("\n" + "=" * 60)
    print("🌐 Flask API Testing")
    print("   Note: Make sure Flask server is running (python app_flask.py)")
    print("   Press Enter to test API, or 's' to skip...")
    
    user_input = input().strip().lower()
    if user_input != 's':
        if not test_flask_api():
            all_tests_passed = False
    else:
        print("⏭️  Skipped Flask API tests")
    
    # Final results
    print("\n" + "=" * 60)
    if all_tests_passed:
        print("🎉 ALL TESTS PASSED!")
        print("✅ Your movie recommendation system is ready to use!")
        print("\n🚀 To start the application:")
        print("   1. Run: python app_flask.py")
        print("   2. Open: http://localhost:5000")
        print("   3. Enjoy discovering movies! 🎬")
    else:
        print("❌ SOME TESTS FAILED!")
        print("   Please check the errors above and fix them.")
        print("   Make sure all files are in place and dependencies are installed.")
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    main()
