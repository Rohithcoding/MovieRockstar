import requests
from typing import Dict, List, Optional, Union
import json
import os
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables
load_dotenv()

# Initialize OpenAI client
openai_client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

class StreamingService:
    def __init__(self, tmdb_api_key: str):
        self.tmdb_api_key = tmdb_api_key
        self.base_url = "https://api.themoviedb.org/3"
        self.headers = {
            "Authorization": f"Bearer {tmdb_api_key}",
            "Content-Type": "application/json;charset=utf-8"
        }

    def get_streaming_links(self, content_id: int, content_type: str = 'movie', title: str = None, year: str = None) -> Dict:
        """
        Get streaming links for a movie or TV show with AI-powered recommendations
        
        Args:
            content_id: TMDB content ID
            content_type: 'movie' or 'tv'
            title: Title of the content (for AI recommendations)
            year: Release year (for AI recommendations)
            
        Returns:
            Dict containing streaming links and AI recommendations
        """
        try:
            # First get the TMDB watch providers
            response = requests.get(
                f"{self.base_url}/{content_type}/{content_id}/watch/providers",
                headers={"Authorization": f"Bearer {self.tmdb_api_key}"}
            )
            response.raise_for_status()
            providers = response.json().get('results', {})
            
            # Process providers
            streaming_links = {
                'stream': [],
                'rent': [],
                'buy': []
            }
            
            # Check US providers first, then other regions
            for region in ['US', 'GB', 'CA', 'IN']:
                if region in providers:
                    region_data = providers[region]
                    for link_type in ['flatrate', 'rent', 'buy']:
                        if link_type in region_data:
                            for provider in region_data[link_type]:
                                streaming_links[link_type if link_type != 'flatrate' else 'stream'].append({
                                    'provider_name': provider.get('provider_name', 'Unknown'),
                                    'logo_path': f"https://image.tmdb.org/t/p/w92{provider.get('logo_path', '')}",
                                    'provider_id': provider.get('provider_id'),
                                    'type': link_type if link_type != 'flatrate' else 'stream',
                                    'url': self._get_streaming_url(content_id, content_type, provider.get('provider_id'))
                                })
            
            # Add AI-powered recommendations if title is provided
            if title and os.getenv('OPENAI_API_KEY'):
                try:
                    # Get AI recommendations
                    ai_response = openai_client.chat.completions.create(
                        model="gpt-3.5-turbo",
                        messages=[
                            {"role": "system", "content": "You are a helpful assistant that provides streaming recommendations."},
                            {"role": "user", "content": f"Provide a brief recommendation for watching '{title}' {f'({year}) ' if year else ''}based on its availability on streaming platforms. Keep it under 100 words."}
                        ],
                        temperature=0.7,
                        max_tokens=150
                    )
                    
                    streaming_links['ai_recommendation'] = ai_response.choices[0].message.content.strip()
                    
                except Exception as ai_error:
                    print(f"Error getting AI recommendations: {str(ai_error)}")
                    streaming_links['ai_recommendation'] = "AI recommendations are currently unavailable."
            
            return streaming_links
            
        except Exception as e:
            print(f"Error getting streaming links: {str(e)}")
            return {'error': str(e)}
    
    def _get_streaming_url(self, content_id: int, content_type: str, provider_id: int) -> str:
        """Generate streaming URL based on provider"""
        # Default fallback URL
        base_url = f"https://www.themoviedb.org/{content_type}/{content_id}/watch"
        
        # Map of provider IDs to their streaming URLs
        provider_urls = {
            # Netflix
            8: "https://www.netflix.com/title/{tmdb_id}",
            # Amazon Prime
            119: "https://www.primevideo.com/detail/{tmdb_id}",
            # Disney+
            337: "https://www.disneyplus.com/movies/{tmdb_id}",
            # Hulu
            15: "https://www.hulu.com/movie/{tmdb_id}",
            # HBO Max
            384: "https://play.hbomax.com/feature/{tmdb_id}",
            # Apple TV+
            350: "https://tv.apple.com/movie/{tmdb_id}",
            # YouTube
            192: "https://www.youtube.com/results?search_query={title}",
            # Google Play Movies
            3: "https://play.google.com/store/movies/details?id={tmdb_id}",
            # Vudu
            7: "https://www.vudu.com/content/movies/details/{title}/{tmdb_id}",
            # Microsoft Store
            68: "https://www.microsoft.com/en-us/p/{title}/{tmdb_id}"
        }
        
        if provider_id in provider_urls:
            return provider_urls[provider_id].format(
                tmdb_id=content_id,
                title=f"{content_type}_{content_id}"
            )
        
        return base_url

    def get_video_embeds(self, content_id: int, content_type: str = 'movie') -> List[Dict]:
        """Get video embeds (trailers, teasers, etc.)"""
        try:
            response = requests.get(
                f"{self.base_url}/{content_type}/{content_id}/videos",
                headers={"Authorization": f"Bearer {self.tmdb_api_key}"}
            )
            response.raise_for_status()
            videos = response.json().get('results', [])
            
            embeds = []
            for video in videos:
                if video.get('site') == 'YouTube':
                    embeds.append({
                        'name': video.get('name', 'Video'),
                        'key': video.get('key'),
                        'type': video.get('type', 'Trailer'),
                        'url': f"https://www.youtube.com/embed/{video.get('key')}"
                    })
            
            return embeds
            
        except Exception as e:
            print(f"Error getting video embeds: {str(e)}")
            return []

# Example usage
if __name__ == "__main__":
    import os
    from dotenv import load_dotenv
    
    load_dotenv()
    tmdb_api_key = os.getenv('TMDB_API_KEY')
    
    if not tmdb_api_key:
        print("Please set TMDB_API_KEY in your .env file")
    else:
        streaming = StreamingService(tmdb_api_key)
        
        # Example: Get streaming links for a movie (Avengers: Endgame)
        print("\nStreaming links for Avengers: Endgame (Movie ID: 299534):")
        print(json.dumps(streaming.get_streaming_links(299534, 'movie'), indent=2))
        
        # Example: Get video embeds for the same movie
        print("\nVideo embeds for Avengers: Endgame (Movie ID: 299534):")
        print(json.dumps(streaming.get_video_embeds(299534, 'movie'), indent=2))
