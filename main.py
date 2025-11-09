import aiohttp
import asyncio
import logging
import traceback
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
import requests
import os
from pathlib import Path
from typing import List, Dict, Optional, Any
from datetime import datetime

app = FastAPI(
    title="Movie Rockstar",
    debug=True,
    docs_url="/docs",
    redoc_url=None
)

# Add middleware for better error handling
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    try:
        response = await call_next(request)
        return response
    except Exception as e:
        logger.error(f"Unhandled exception: {str(e)}")
        logger.error(traceback.format_exc())
        return JSONResponse(
            status_code=500,
            content={
                "detail": "Internal server error",
                "error": str(e),
                "traceback": traceback.format_exc()
            }
        )

# Get base directory
BASE_DIR = Path(__file__).parent

# Mount static files
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

# TMDB API Configuration
TMDB_API_KEY = "824517fc3eeb54a8859418c6c4b71775"  # Keep as fallback if needed
TMDB_IMAGE_BASE_URL = "https://image.tmdb.org/t/p/"

class TMDBClient:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.themoviedb.org/3"
        self.image_base_url = TMDB_IMAGE_BASE_URL
        self.headers = {
            "Content-Type": "application/json;charset=utf-8"
        }
        self.session = None

    async def get_session(self):
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession()
        return self.session

    async def _make_request(
        self, 
        endpoint: str, 
        params: Optional[Dict] = None, 
        max_retries: int = 3
    ) -> Any:
        """
        Make an async HTTP request to TMDB API with retry logic.
        
        Args:
            endpoint: TMDB API endpoint (e.g., 'movie/popular')
            params: Query parameters
            max_retries: Maximum retry attempts
            
        Returns:
            Parsed JSON response
            
        Raises:
            HTTPException: If all retries fail
        """
        # Initialize params and headers
        params = params or {}
        params['api_key'] = self.api_key
        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/json;charset=utf-8'
        }
        
        # Build URL
        base_url = self.base_url.rstrip('/')
        endpoint = endpoint.lstrip('/')
        url = f"{base_url}/{endpoint}"
        
        # Initialize last exception
        last_exception = None
        
        # Retry loop
        for attempt in range(max_retries):
            try:
                # Get or create session
                session = await self.get_session()
                
                # Log the request
                logger.debug(f"Request attempt {attempt + 1}/{max_retries}: {url} with params: {params}")
                
                # Make request with timeout
                timeout = aiohttp.ClientTimeout(total=10)
                async with session.get(
                    url,
                    params=params,
                    headers=headers,
                    timeout=timeout
                ) as response:
                    
                    # Make the request
                    async with session.get(
                        url,
                        params=params,
                        headers={
                            'Accept': 'application/json',
                            'Content-Type': 'application/json;charset=utf-8'
                        },
                        timeout=aiohttp.ClientTimeout(total=10)
                    ) as response:
                        # Handle successful response
                        if response.status == 200:
                            return await response.json()
                            
                        # Handle rate limiting
                        if response.status == 429:
                            retry_after = int(response.headers.get('Retry-After', 1))
                            print(f"Rate limited. Waiting {retry_after} seconds...")
                            await asyncio.sleep(retry_after)
                            continue
                        
                        # Handle other errors
                        error_text = await response.text()
                        print(f"TMDB API error: {response.status} - {error_text}")
                        
                        if attempt == max_retries - 1:
                            raise HTTPException(
                                status_code=response.status,
                                detail=f"TMDB API error: {response.status} - {error_text}"
                            )
                        
                        # Exponential backoff
                        backoff = 1 + random.random() * (2 ** attempt)
                        print(f"Retrying in {backoff:.2f} seconds...")
                        await asyncio.sleep(backoff)
            
            except (aiohttp.ClientError, asyncio.TimeoutError) as e:
                last_exception = e
                print(f"Request failed (attempt {attempt + 1}/{max_retries}): {str(e)}")
                
                if attempt == max_retries - 1:
                    raise HTTPException(
                        status_code=500,
                        detail=f"Failed to fetch data from TMDB after {max_retries} attempts: {str(e)}"
                    )
                
                # Exponential backoff for network errors
                backoff = 1 + random.random() * (2 ** attempt)
                print(f"Retrying in {backoff:.2f} seconds...")
                await asyncio.sleep(backoff)
        
        # This should never be reached due to the raise in the except block
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch data from TMDB after {max_retries} attempts"
        ) 
                        headers=headers, 
                        timeout=aiohttp.ClientTimeout(total=15)
                    ) as response:
                        response_text = await response.text()
                        print(f"Response status: {response.status}")
                        print(f"Response headers: {dict(response.headers)}")
                        print(f"Response content: {response_text[:200]}...")  # Print first 200 chars
                        
                        if response.status == 200:
                            try:
                                return await response.json()
                            except Exception as e:
                                print(f"Error parsing JSON response: {e}")
                                print(f"Response text: {response_text}")
                                return {"results": []}
                                
                        elif response.status == 204:  # No Content
                            print(f"Received 204 No Content from TMDB API for {endpoint}")
                            return {"results": []}  # Return empty results to prevent errors
                            
                        elif response.status == 429:  # Rate limit hit
                            retry_after = int(response.headers.get('Retry-After', 5))
                            print(f"Rate limited. Retrying after {retry_after} seconds...")
                            await asyncio.sleep(retry_after)
                            continue
                            
                        else:
                            error_msg = f"Error in _make_request (attempt {attempt + 1}/{max_retries}): {response.status} - {response_text}"
                            print(error_msg)
                            
                            if attempt < max_retries - 1 and response.status >= 500:
                                # Exponential backoff with jitter
                                backoff = (2 ** attempt) + random.uniform(0, 1)
                                print(f"Retrying in {backoff:.2f} seconds...")
                                await asyncio.sleep(backoff)
                                continue
                                
                            return {
                                "status_code": response.status, 
                                "status_message": f"Error making request: {response_text}",
                                "results": []  # Ensure empty results to prevent template errors
                            }
            except (aiohttp.ClientError, asyncio.TimeoutError) as e:
                last_exception = e
                print(f"Request failed (attempt {attempt + 1}/{max_retries}): {str(e)}")
                if attempt < max_retries - 1:
                    # Exponential backoff with jitter
                    backoff = (2 ** attempt) + random.uniform(0, 1)
                    await asyncio.sleep(backoff)
                continue
            except Exception as e:
                last_exception = e
                error_msg = f"Unexpected error in _make_request (attempt {attempt + 1}/{max_retries}): {str(e)}"
                print(error_msg)
                traceback.print_exc()
                if attempt < max_retries - 1:
                    backoff = (2 ** attempt) + random.uniform(0, 1)
                    await asyncio.sleep(backoff)
                continue
        
        # If we've exhausted all retries
        error_msg = str(last_exception) if last_exception else "Unknown error"
        print(f"All {max_retries} attempts failed. Last error: {error_msg}")
        return {
            "status_code": 500, 
            "status_message": f"Error making request after {max_retries} attempts: {error_msg}"
        }

    async def get_trending(self, media_type: str = "all", time_window: str = "day") -> List[Dict]:
        endpoint = f"trending/{media_type}/{time_window}"
        data = await self._make_request(endpoint)
        return data.get("results", []) if data else []

    async def search(self, query: str, media_type: str = "multi", page: int = 1) -> Dict:
        endpoint = f"search/{media_type}"
        params = {
            "query": query,
            "page": page,
            "include_adult": "false"
        }
        return await self._make_request(endpoint, params) or {}

    async def get_movie_details(self, movie_id: int) -> Dict:
        endpoint = f"movie/{movie_id}"
        params = {
            "append_to_response": "videos,credits,recommendations,watch/providers,similar"
        }
        return await self._make_request(endpoint, params) or {}

    async def get_tv_details(self, tv_id: int) -> Dict:
        endpoint = f"tv/{tv_id}"
        params = {
            "append_to_response": "videos,credits,recommendations,watch/providers,similar"
        }
        return await self._make_request(endpoint, params) or {}

    async def get_popular_movies(self, page: int = 1) -> List[Dict]:
        endpoint = "movie/popular"
        params = {"page": page}
        data = await self._make_request(endpoint, params)
        return data.get("results", []) if data else []
        
    async def get_popular_tv(self, page: int = 1) -> List[Dict]:
        endpoint = "tv/popular"
        params = {"page": page}
        data = await self._make_request(endpoint, params)
        return data.get("results", []) if data else []

    async def get_top_rated_movies(self, page: int = 1) -> List[Dict]:
        endpoint = "movie/top_rated"
        params = {"page": page}
        data = await self._make_request(endpoint, params)
        return data.get("results", []) if data else []
        
    async def get_top_rated_tv(self, page: int = 1) -> List[Dict]:
        endpoint = "tv/top_rated"
        params = {"page": page}
        data = await self._make_request(endpoint, params)
        return data.get("results", []) if data else []
        
    async def get_watch_providers(self, media_type: str, media_id: int) -> Dict:
        """Get watch providers for a movie or TV show."""
        endpoint = f"{media_type}/{media_id}/watch/providers"
        return await self._make_request(endpoint) or {}
        
    async def get_movie_details(self, movie_id: int) -> Dict:
        """Get detailed information about a specific movie."""
        endpoint = f"movie/{movie_id}"
        return await self._make_request(endpoint) or {}
        
    async def get_tv_details(self, tv_id: int) -> Dict:
        """Get detailed information about a specific TV show."""
        endpoint = f"tv/{tv_id}"
        return await self._make_request(endpoint) or {}

# Initialize TMDB client with API key
tmdb_client = TMDBClient(api_key=TMDB_API_KEY)

# Test Endpoint
@app.get("/test")
async def test():
    return {"message": "Test endpoint working"}

# Health Check Endpoint
@app.get("/health")
async def health_check():
    return {"status": "ok", "message": "Service is running"}

# API Endpoints
@app.get("/api/trending")
async def get_trending(media_type: str = "movie", time_window: str = "day", page: int = 1):
    results = await tmdb_client.get_trending(media_type, time_window, page)
    return JSONResponse({"results": results})

@app.get("/api/search")
async def search(query: str, media_type: str = "movie", page: int = 1):
    results = await tmdb_client.search(query, media_type, page)
    return JSONResponse(results)

@app.get("/api/movie/{movie_id}")
async def get_movie(movie_id: int):
    movie = await tmdb_client.get_movie_details(movie_id)
    if not movie:
        raise HTTPException(status_code=404, detail="Movie not found")
    return JSONResponse(movie)

@app.get("/api/movies/popular")
async def get_popular_movies(page: int = 1):
    results = await tmdb_client.get_popular_movies(page)
    return JSONResponse({"results": results})

@app.get("/api/movies/top_rated")
async def get_top_rated_movies(page: int = 1):
    results = await tmdb_client.get_top_rated_movies(page)
    return JSONResponse({"results": results})

# Static files for favicon
@app.get('/favicon.ico', include_in_schema=False)
async def favicon():
    from fastapi.responses import FileResponse
    import os
    favicon_path = os.path.join(BASE_DIR, "static", "favicon.ico")
    if os.path.exists(favicon_path):
        return FileResponse(favicon_path)
    return ""

# Frontend Routes
@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    try:
        logger.info("Root endpoint called")
        
        # Initialize with empty lists in case of errors
        trending_movies = {"results": []}
        trending_tv = {"results": []}
        popular_movies = {"results": []}
        top_rated_movies = {"results": []}
        
        # Get data with individual error handling for each API call
        try:
            trending_movies = await tmdb_client.get_trending("movie", "day") or {"results": []}
        except Exception as e:
            logger.error(f"Error getting trending movies: {str(e)}")
            
        try:
            trending_tv = await tmdb_client.get_trending("tv", "day") or {"results": []}
        except Exception as e:
            logger.error(f"Error getting trending TV: {str(e)}")
            
        try:
            popular_movies = await tmdb_client.get_popular_movies() or {"results": []}
        except Exception as e:
            logger.error(f"Error getting popular movies: {str(e)}")
            
        try:
            top_rated_movies = await tmdb_client.get_top_rated_movies() or {"results": []}
        except Exception as e:
            logger.error(f"Error getting top rated movies: {str(e)}")
        
        # Log the data being sent to the template
        logger.info(f"Sending data to template - Movies: {len(trending_movies.get('results', []))}, TV: {len(trending_tv.get('results', []))}")
        
        return templates.TemplateResponse("index.html", {
            "request": request,
            "trending_movies": trending_movies.get("results", [])[:10],
            "trending_tv": trending_tv.get("results", [])[:10],
            "popular_movies": popular_movies.get("results", [])[:10],
            "top_rated_movies": top_rated_movies.get("results", [])[:10],
            "title": "Movie Rockstar - Discover Movies & TV Shows"
        })
        
    except Exception as e:
        error_msg = f"Error in read_root: {str(e)}\n{traceback.format_exc()}"
        logger.error(error_msg)
        # Return a simple error page instead of raising an exception
        return templates.TemplateResponse("error.html", {
            "request": request,
            "error": "We're having trouble loading the homepage. Please try again later.",
            "details": str(e)
        }, status_code=500)
        print(f"Error in read_root: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Internal Server Error")

@app.get("/movie/{movie_id}", response_class=HTMLResponse)
async def read_movie(request: Request, movie_id: int):
    try:
        print(f"\n=== Starting request for movie ID: {movie_id} ===")
        
        # Fetch movie details
        print("\n1. Fetching movie details...")
        movie = await tmdb_client.get_movie_details(movie_id)
        print(f"Movie data: {bool(movie)}")
        
        if not movie or 'status_code' in movie:
            error_msg = f"Movie not found. TMDB Response: {movie}"
            print(f"Error: {error_msg}")
            raise HTTPException(status_code=404, detail=error_msg)
        
        # Get videos (trailers)
        print("\n2. Fetching videos...")
        videos = {}
        try:
            videos = await tmdb_client._make_request(f"movie/{movie_id}/videos") or {}
            print(f"Videos found: {len(videos.get('results', []))}")
        except Exception as e:
            print(f"Error fetching videos: {str(e)}")
            videos = {}
        
        trailer = next((v for v in videos.get('results', []) 
                       if v.get('type') == 'Trailer' and v.get('site') == 'YouTube'), None)
        print(f"Trailer found: {trailer is not None}")
        
        # Get streaming providers
        print("\n3. Fetching providers...")
        providers = {}
        try:
            providers = await tmdb_client._make_request(f"movie/{movie_id}/watch/providers") or {}
            print(f"Providers response: {bool(providers.get('results'))}")
        except Exception as e:
            print(f"Error fetching providers: {str(e)}")
            providers = {}
        
        # Get streaming links
        streaming_links = {}
        try:
            if providers.get('results', {}).get('US'):
                us_providers = providers['results']['US']
                print(f"US providers: {us_providers.keys()}")
                
                if us_providers.get('flatrate'):
                    streaming_links['stream'] = [{
                        'provider_name': p.get('provider_name', 'Unknown'),
                        'logo_path': f"{TMDB_IMAGE_BASE}w92{p.get('logo_path', '')}" if p.get('logo_path') else '',
                        'link': f"https://www.themoviedb.org/movie/{movie_id}/watch?locale=US"
                    } for p in us_providers.get('flatrate', [])]
                
                if us_providers.get('rent'):
                    streaming_links['rent'] = [{
                        'provider_name': p.get('provider_name', 'Unknown'),
                        'logo_path': f"{TMDB_IMAGE_BASE}w92{p.get('logo_path', '')}" if p.get('logo_path') else '',
                        'link': f"https://www.themoviedb.org/movie/{movie_id}/watch?locale=US"
                    } for p in us_providers.get('rent', [])]
                    
                if us_providers.get('buy'):
                    streaming_links['buy'] = [{
                        'provider_name': p.get('provider_name', 'Unknown'),
                        'logo_path': f"{TMDB_IMAGE_BASE}w92{p.get('logo_path', '')}" if p.get('logo_path') else '',
                        'link': f"https://www.themoviedb.org/movie/{movie_id}/watch?locale=US"
                    } for p in us_providers.get('buy', [])]
            
            print(f"Streaming links: {list(streaming_links.keys())}")
            
        except Exception as e:
            print(f"Error processing providers: {str(e)}")
            import traceback
            traceback.print_exc()
        
        # Get credits and similar movies
        print("\n4. Fetching credits and similar movies...")
        credits = {}
        similar = {}
        try:
            credits = await tmdb_client._make_request(f"movie/{movie_id}/credits") or {}
            similar = await tmdb_client._make_request(f"movie/{movie_id}/similar") or {}
            print(f"Credits: {len(credits.get('cast', []))} cast, {len(credits.get('crew', []))} crew")
            print(f"Similar movies: {len(similar.get('results', []))}")
        except Exception as e:
            print(f"Error fetching additional data: {str(e)}")
            
        print("\n=== All data fetched successfully ===\n")
        
        return templates.TemplateResponse(
            "movie.html", 
            {
                "request": request,
                "movie": movie,
                "credits": credits,
                "similar": similar,
                "trailer": trailer,
                "providers": providers,
                "streaming_links": streaming_links,
                "config": {
                    "TMDB_IMAGE_BASE": TMDB_IMAGE_BASE_URL,
                    "YOUTUBE_EMBED_URL": "https://www.youtube.com/embed/"
                }
            }
        )
    except HTTPException as he:
        raise he
    except Exception as e:
        print(f"Error in read_movie: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

@app.get("/search", response_class=HTMLResponse)
async def search_movies(request: Request, q: str = "", page: int = 1):
    try:
        if not q:
            return RedirectResponse(url="/")
            
        results = await tmdb_client.search(q, page=page)
        return templates.TemplateResponse(
            "search.html",
            {
                "request": request,
                "query": q,
                "results": results,
                "current_page": page,
                "config": {
                    "TMDB_IMAGE_BASE": TMDB_IMAGE_BASE_URL
                }
            }
        )
    except Exception as e:
        print(f"Search error: {str(e)}")
        raise HTTPException(status_code=500, detail="Search failed")

@app.get("/watch/{media_type}/{media_id}", response_class=HTMLResponse)
async def watch_media(request: Request, media_type: str, media_id: int):
    try:
        # Validate media type
        if media_type not in ["movie", "tv"]:
            raise HTTPException(status_code=400, detail="Invalid media type. Must be 'movie' or 'tv'")
            
        # Get media details
        if media_type == "movie":
            media = await tmdb_client.get_movie_details(media_id)
            title = media.get("title", "")
            release_date = media.get("release_date", "")
            media_url = f"https://www.themoviedb.org/movie/{media_id}/watch"
            credits = await tmdb_client._make_request(f"movie/{media_id}/credits") or {}
            year = release_date.split('-')[0] if release_date else ""
        else:
            media = await tmdb_client.get_tv_details(media_id)
            title = media.get("name", "")
            release_date = media.get("first_air_date", "")
            media_url = f"https://www.themoviedb.org/tv/{media_id}/watch"
            credits = await tmdb_client._make_request(f"tv/{media_id}/credits") or {}
            year = release_date.split('-')[0] if release_date else ""
            
        if not media or 'status_code' in media:
            raise HTTPException(status_code=404, detail=f"{media_type.capitalize()} not found")
        
        # Get AI-powered streaming links
        ai_links = []
        if os.getenv('OPENAI_API_KEY'):
            try:
                from openai_utils import OpenAIService
                openai_service = OpenAIService()
                ai_links = await asyncio.get_event_loop().run_in_executor(
                    None,
                    lambda: openai_service.get_direct_streaming_links(title, media_type, year)
                )
            except Exception as e:
                print(f"Error getting AI streaming links: {str(e)}")
        
        # Get watch providers from TMDB as fallback
        providers = await tmdb_client.get_watch_providers(media_type, media_id)
        
        # Format streaming links
        streaming_links = {}
        
        # Add AI-powered links first
        if ai_links:
            streaming_links['ai_stream'] = [{
                'provider_name': link.get('provider', 'Streaming Service'),
                'logo_path': f"/static/images/{link.get('provider', '').lower().replace(' ', '-')}.png"
                            if link.get('provider') else '/static/images/no-logo.png',
                'link': link.get('url', media_url),
                'type': link.get('type', 'subscription'),
                'price': link.get('price', 'Check Price'),
                'quality': link.get('quality', 'HD')
            } for link in ai_links if link.get('url')]
        
        # Fallback to TMDB providers if no AI links found
        if not streaming_links.get('ai_stream') and providers and providers.get('results', {}).get('US'):
            us_providers = providers['results']['US']
            
            if us_providers.get('flatrate'):
                streaming_links['stream'] = [{
                    'provider_name': p.get('provider_name'),
                    'logo_path': f"{TMDB_IMAGE_BASE_URL}w92{p.get('logo_path', '')}" if p.get('logo_path') else '/static/images/no-logo.png',
                    'link': media_url,
                    'type': 'subscription',
                    'price': 'Included with subscription',
                    'quality': 'HD'
                } for p in us_providers['flatrate']]
            
            if us_providers.get('rent'):
                streaming_links['rent'] = [{
                    'provider_name': p.get('provider_name'),
                    'logo_path': f"{TMDB_IMAGE_BASE_URL}w92{p.get('logo_path', '')}" if p.get('logo_path') else '/static/images/no-logo.png',
                    'link': media_url
                } for p in us_providers['rent']]
                
            if us_providers.get('buy'):
                streaming_links['buy'] = [{
                    'provider_name': p.get('provider_name'),
                    'logo_path': f"{TMDB_IMAGE_BASE_URL}w92{p.get('logo_path', '')}" if p.get('logo_path') else '/static/images/no-logo.png',
                    'link': media_url
                } for p in us_providers['buy']]
        
        # If no providers found, show TMDB link as fallback
        if not streaming_links:
            streaming_links['stream'] = [{
                'provider_name': 'TMDB',
                'logo_path': f"{TMDB_IMAGE_BASE_URL}w92/9A1JSVmSxsyaBK4SUFsYVFqbTWf.png",
                'link': media_url
            }]

        # Prepare context with proper variable names for the template
        context = {
            "request": request,
            "media_type": media_type,
            "media": media,  # Single media object for both movies and TV shows
            "media_url": media_url,
            "streaming_links": streaming_links,
            "credits": credits,
            "config": {
                "TMDB_IMAGE_BASE": TMDB_IMAGE_BASE_URL
            },
            # Add title for the template
            "title": media.get("title" if media_type == "movie" else "name", "")
        }
        
        return templates.TemplateResponse("watch.html", context)
    except HTTPException as he:
        raise he
    except Exception as e:
        print(f"Error in watch_media: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Internal Server Error")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
