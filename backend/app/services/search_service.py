from fastapi import UploadFile
import logging
from typing import List, Dict, Optional

logger = logging.getLogger(__name__)

# Check if CLIP is available
try:
    from app.services.clip import get_image_embedding, get_text_embedding, calculate_similarity
    CLIP_AVAILABLE = True
    logger.info("CLIP services available for search")
except ImportError as e:
    logger.warning(f"CLIP services not available for search: {e}")
    CLIP_AVAILABLE = False
    
    # Provide dummy functions when CLIP is not available
    async def get_image_embedding(file):
        raise Exception("CLIP library not available. Install with: pip install git+https://github.com/openai/CLIP.git")
    
    def get_text_embedding(text: str):
        raise Exception("CLIP library not available. Install with: pip install git+https://github.com/openai/CLIP.git")
    
    def calculate_similarity(emb1, emb2):
        raise Exception("CLIP library not available. Install with: pip install git+https://github.com/openai/CLIP.git")

# In-memory storage for image embeddings (use proper database in production)
image_database: List[Dict] = []

async def search_similar_images(
    file: Optional[UploadFile] = None, 
    query: Optional[str] = None,
    limit: int = 10,
    similarity_threshold: float = 0.1
) -> List[Dict]:
    """Search for similar images using CLIP embeddings"""
    try:
        if not file and not query:
            raise ValueError("Either file or query must be provided")
        
        if len(image_database) == 0:
            logger.warning("Image database is empty")
            return []
        
        # Get query embedding
        if file:
            query_embedding = await get_image_embedding(file)
            query_type = "image"
        else:
            query_embedding = get_text_embedding(query)
            query_type = "text"
        
        # Calculate similarities
        similarities = []
        for idx, stored_image in enumerate(image_database):
            similarity = calculate_similarity(query_embedding, stored_image["embedding"])
            
            if similarity >= similarity_threshold:
                similarities.append({
                    "id": stored_image.get("id", idx),
                    "url": stored_image.get("url", f"image_{idx}"),
                    "similarity": similarity,
                    "metadata": stored_image.get("metadata", {})
                })
        
        # Sort by similarity (descending) and limit results
        similarities.sort(key=lambda x: x["similarity"], reverse=True)
        results = similarities[:limit]
        
        logger.info(f"Found {len(results)} similar images for {query_type} query")
        return results
        
    except Exception as e:
        logger.error(f"Error searching similar images: {e}")
        raise Exception(f"Failed to search images: {str(e)}")

async def add_image_to_database(file: UploadFile, image_url: str, metadata: Optional[Dict] = None):
    """Add image embedding to the search database"""
    try:
        embedding = await get_image_embedding(file)
        
        image_entry = {
            "id": len(image_database),
            "url": image_url,
            "embedding": embedding,
            "metadata": metadata or {}
        }
        
        image_database.append(image_entry)
        logger.info(f"Added image to database: {image_url}")
        
        return image_entry["id"]
        
    except Exception as e:
        logger.error(f"Error adding image to database: {e}")
        raise Exception(f"Failed to add image: {str(e)}")

def get_database_stats() -> Dict:
    """Get statistics about the image database"""
    return {
        "total_images": len(image_database),
        "embedding_dimension": len(image_database[0]["embedding"]) if image_database else 0
    }

def clear_database():
    """Clear the image database (for testing/development)"""
    global image_database
    image_database = []
    logger.info("Cleared image database")
