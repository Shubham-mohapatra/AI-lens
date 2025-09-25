import os
import logging
from typing import List, Dict, Optional
import requests
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

PIXABAY_API_KEY = os.getenv("PIXABAY_API_KEY", "")
PIXABAY_ENDPOINT = "https://pixabay.com/api/"

async def search_similar_images_pixabay(
    query: str,
    count: int = 10,
    image_type: str = "photo",
    category: str = "all",
    min_width: int = 640
) -> List[Dict]:
    """
    Search for similar images using Pixabay API (FREE - 20,000 requests/month)
    """
    if not PIXABAY_API_KEY:
        # If no API key, use a demo mode with placeholder data
        logger.warning("No Pixabay API key found. Using demo mode with sample results.")
        return get_demo_results(query, count)
    
    try:
        params = {
            'key': PIXABAY_API_KEY,
            'q': query,
            'image_type': image_type,  # "all", "photo", "illustration", "vector"
            'orientation': 'all',      # "all", "horizontal", "vertical"
            'category': category,      # "backgrounds", "fashion", "nature", "science", "education", etc.
            'min_width': min_width,
            'min_height': 480,
            'per_page': min(count, 200),  # Pixabay allows max 200 per request
            'safesearch': 'true',
            'order': 'popular'         # "popular", "latest", "ec" (Editor's Choice)
        }
        
        logger.info(f"Searching Pixabay for images with query: '{query}'")
        
        response = requests.get(PIXABAY_ENDPOINT, params=params, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        images = data.get('hits', [])
        
        # Format results
        results = []
        for img in images:
            result = {
                "url": img.get("largeImageURL", img.get("fullHDURL", img.get("webformatURL", ""))),
                "thumbnail": img.get("previewURL", ""),
                "title": img.get("tags", f"Image about {query}"),
                "source": f"pixabay.com/photos/{img.get('id', '')}",
                "width": img.get("imageWidth", 0),
                "height": img.get("imageHeight", 0),
                "size": f"{img.get('imageSize', 0)} bytes",
                "downloads": img.get("downloads", 0),
                "likes": img.get("likes", 0),
                "user": img.get("user", "Unknown"),
                "tags": img.get("tags", "").split(", ")
            }
            results.append(result)
        
        logger.info(f"Found {len(results)} images from Pixabay")
        return results
        
    except requests.exceptions.RequestException as e:
        logger.error(f"Error calling Pixabay API: {e}")
        # Fallback to demo mode
        logger.info("Falling back to demo mode")
        return get_demo_results(query, count)
    except Exception as e:
        logger.error(f"Error processing Pixabay results: {e}")
        return get_demo_results(query, count)

def get_demo_results(query: str, count: int) -> List[Dict]:
    """
    Get demo/placeholder results when API is not available
    """
    try:
        logger.info(f"Generating {count} demo results for query: '{query}'")
        
        demo_images = [
            {
                "url": f"https://via.placeholder.com/800x600/0066cc/ffffff?text={query.replace(' ', '+')}+1",
                "thumbnail": f"https://via.placeholder.com/150x150/0066cc/ffffff?text=1",
                "title": f"Demo image about {query} #1",
                "source": "demo.placeholder.com",
                "width": 800,
                "height": 600,
                "size": "Demo image",
                "downloads": 100,
                "likes": 50,
                "user": "Demo User",
                "tags": query.split() + ["demo", "placeholder"]
            },
            {
                "url": f"https://via.placeholder.com/800x600/cc6600/ffffff?text={query.replace(' ', '+')}+2",
                "thumbnail": f"https://via.placeholder.com/150x150/cc6600/ffffff?text=2",
                "title": f"Demo image about {query} #2",
                "source": "demo.placeholder.com",
                "width": 800,
                "height": 600,
                "size": "Demo image",
                "downloads": 80,
                "likes": 40,
                "user": "Demo User",
                "tags": query.split() + ["demo", "placeholder"]
            },
            {
                "url": f"https://via.placeholder.com/800x600/009966/ffffff?text={query.replace(' ', '+')}+3",
                "thumbnail": f"https://via.placeholder.com/150x150/009966/ffffff?text=3",
                "title": f"Demo image about {query} #3",
                "source": "demo.placeholder.com",
                "width": 800,
                "height": 600,
                "size": "Demo image",
                "downloads": 120,
                "likes": 60,
                "user": "Demo User",
                "tags": query.split() + ["demo", "placeholder"]
            },
            {
                "url": f"https://via.placeholder.com/800x600/cc0066/ffffff?text={query.replace(' ', '+')}+4",
                "thumbnail": f"https://via.placeholder.com/150x150/cc0066/ffffff?text=4",
                "title": f"Demo image about {query} #4",
                "source": "demo.placeholder.com",
                "width": 800,
                "height": 600,
                "size": "Demo image",
                "downloads": 90,
                "likes": 45,
                "user": "Demo User",
                "tags": query.split() + ["demo", "placeholder"]
            },
            {
                "url": f"https://via.placeholder.com/800x600/6600cc/ffffff?text={query.replace(' ', '+')}+5",
                "thumbnail": f"https://via.placeholder.com/150x150/6600cc/ffffff?text=5",
                "title": f"Demo image about {query} #5",
                "source": "demo.placeholder.com",
                "width": 800,
                "height": 600,
                "size": "Demo image",
                "downloads": 110,
                "likes": 55,
                "user": "Demo User",
                "tags": query.split() + ["demo", "placeholder"]
            }
        ]
        
        # Ensure we have enough results
        if count <= len(demo_images):
            result_list = demo_images[:count]
        else:
            # Repeat the demo images to meet the requested count
            multiplier = (count // len(demo_images)) + 1
            extended_list = demo_images * multiplier
            result_list = extended_list[:count]
        
        logger.info(f"Generated {len(result_list)} demo results")
        return result_list
        
    except Exception as e:
        logger.error(f"Error generating demo results: {e}")
        # Return at least one result even if there's an error
        return [{
            "url": f"https://via.placeholder.com/800x600/999999/ffffff?text=Demo+Error",
            "thumbnail": f"https://via.placeholder.com/150x150/999999/ffffff?text=Error",
            "title": f"Demo error image",
            "source": "demo.error.com",
            "width": 800,
            "height": 600,
            "size": "Error image",
            "downloads": 0,
            "likes": 0,
            "user": "Error User",
            "tags": ["error", "demo"]
        }]
    
    # Return requested number of demo results
    result_list = demo_images * ((count // len(demo_images)) + 1)
    return result_list[:count]

def get_search_suggestions(query: str) -> List[str]:
    """
    Get search suggestions for better image search results
    """
    suggestions = [
        f"{query} high quality",
        f"{query} professional",
        f"{query} beautiful",
        f"{query} nature",
        f"{query} lifestyle"
    ]
    return suggestions[:3]

async def search_by_image_description(description: str, count: int = 10) -> Dict:
    """
    Search for images using a description (from image captioning)
    """
    try:
        # Clean and enhance the description for better search results
        enhanced_query = description.replace("a photo of", "").replace("an image of", "").strip()
        
        # Remove common words that don't help with search
        stop_words = ["the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for", "of", "with", "by"]
        query_words = [word for word in enhanced_query.split() if word.lower() not in stop_words]
        enhanced_query = " ".join(query_words)
        
        results = await search_similar_images_pixabay(
            query=enhanced_query,
            count=count
        )
        
        return {
            "query": enhanced_query,
            "original_description": description,
            "results": results,
            "total_found": len(results),
            "api_used": "pixabay" if PIXABAY_API_KEY else "demo"
        }
        
    except Exception as e:
        logger.error(f"Error in image description search: {e}")
        raise Exception(f"Failed to search by description: {str(e)}")