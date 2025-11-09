import openai
from typing import List, Dict, Optional
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize OpenAI client
openai.api_key = os.getenv('OPENAI_API_KEY')

class OpenAIService:
    def __init__(self, model: str = "gpt-3.5-turbo"):
        self.model = model
        
    def get_direct_streaming_links(self, title: str, content_type: str, year: Optional[int] = None) -> List[Dict]:
        """
        Get direct streaming links using OpenAI
        
        Args:
            title: Title of the movie or TV show
            content_type: 'movie' or 'tv'
            year: Release year (optional)
            
        Returns:
            List of dictionaries containing streaming links and metadata
        """
        try:
            # Prepare the prompt
            prompt = f"""
            You are a streaming platform expert. For the following content, provide direct streaming links 
            from legitimate sources. Only include official streaming platforms.
            
            Title: {title}
            Type: {'Movie' if content_type == 'movie' else 'TV Show'}
            {f'Year: {year}' if year else ''}
            
            Provide a list of streaming platforms where this content is available.
            For each platform, include:
            - Platform name (e.g., Netflix, Amazon Prime, Disney+)
            - Direct URL to watch the content (if possible)
            - Whether it's included with subscription, available to rent, or purchase
            - Price if not included with subscription
            - Video quality (SD, HD, 4K, HDR, etc.)
            
            Format your response as a JSON array of objects with these keys:
            - provider: str (platform name)
            - url: str (direct watch URL)
            - type: str ('subscription', 'rent', 'buy')
            - price: str (e.g., 'Included', '$3.99', 'Not available')
            - quality: str (e.g., 'HD', '4K', 'HDR')
            """
            
            # Call OpenAI API
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that provides direct streaming links for movies and TV shows."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=1000
            )
            
            # Parse the response
            import json
            try:
                content = response.choices[0].message['content'].strip()
                # Clean up the response to ensure it's valid JSON
                content = content.replace('```json', '').replace('```', '').strip()
                links = json.loads(content)
                return links if isinstance(links, list) else []
            except (json.JSONDecodeError, KeyError) as e:
                print(f"Error parsing OpenAI response: {str(e)}")
                return []
                
        except Exception as e:
            print(f"Error getting streaming links from OpenAI: {str(e)}")
            return []
            
    def get_streaming_recommendations(self, title: str, content_type: str, year: Optional[int] = None) -> Dict:
        """
        Get personalized streaming recommendations using OpenAI
        
        Args:
            title: Title of the movie or TV show
            content_type: 'movie' or 'tv'
            year: Release year (optional)
            
        Returns:
            Dict containing streaming recommendations and reasoning
        """
        try:
            # Create the prompt for the API
            prompt = f"""
            Provide streaming recommendations for this {'movie' if content_type == 'movie' else 'TV show'}:
            
            Title: {title}
            Year: {year if year else 'N/A'}
            
            Please provide:
            1. Where to watch it (streaming platforms)
            2. Similar content recommendations
            3. Why someone might enjoy it
            """
            
            # Call OpenAI API
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that provides detailed information about movies and TV shows."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=500
            )
            
            # Parse the response
            content = response.choices[0].message.content
            
            # Try to parse as JSON, fallback to text if needed
            try:
                import json
                return json.loads(content)
            except json.JSONDecodeError:
                return {"response": content}
                
        except Exception as e:
            return {"error": str(e)}
    
    def generate_content_description(self, title: str, content_type: str, details: Dict) -> str:
        """Generate an engaging description for the content"""
        try:
            prompt = f"""
            Write an engaging and concise description for this {'movie' if content_type == 'movie' else 'TV show'}:
            
            Title: {title}
            Overview: {details.get('overview', 'No overview available.')}
            Genres: {', '.join([g['name'] for g in details.get('genres', [])])}
            
            Make it engaging and highlight what makes this content special.
            Keep it under 200 characters.
            """
            
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a creative writer who creates engaging descriptions for movies and TV shows."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.8,
                max_tokens=100
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            return details.get('overview', 'No description available.')

# Example usage
if __name__ == "__main__":
    openai_service = OpenAIService()
    
    # Example: Get recommendations for a movie
    result = openai_service.get_streaming_recommendations(
        title="Inception",
        content_type="movie",
        year=2010
    )
    
    print("OpenAI Recommendations:")
    print(result)
