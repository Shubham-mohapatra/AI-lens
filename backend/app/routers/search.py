# routers/search.py
from fastapi import APIRouter, UploadFile, File, HTTPException, Query
from fastapi.responses import JSONResponse
import time
import logging
from typing import Optional
from app.services.caption import generate_caption
from app.services.pixabay_search import search_by_image_description, search_similar_images_pixabay
from app.models import ImageSearchResponse, ImageSearchResult, ErrorResponse

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/by-image", response_model=ImageSearchResponse)
async def search_by_image(
    file: UploadFile = File(...),
    count: int = Query(10, ge=1, le=50, description="Number of results to return")
):
    """Search for similar images on the internet using an uploaded image"""
    start_time = time.time()
    
    # Validate file type
    if not file.content_type.startswith("image/"):
        raise HTTPException(
            status_code=400,
            detail="File must be an image (JPEG, PNG, etc.)"
        )
    
    # Validate file size (10MB limit)
    if file.size and file.size > 10 * 1024 * 1024:
        raise HTTPException(
            status_code=400,
            detail="File size must be less than 10MB"
        )
    
    try:
        # First, generate a caption for the uploaded image
        logger.info("Generating caption for uploaded image...")
        caption = await generate_caption(file)
        
        # Use the caption to search for similar images on Pixabay
        logger.info(f"Searching for similar images using caption: '{caption}'")
        search_results = await search_by_image_description(caption, count)
        
        # Convert results to the expected format
        similar_images = []
        for result in search_results["results"]:
            similar_images.append(ImageSearchResult(
                url=result["url"],
                thumbnail=result["thumbnail"],
                title=result["title"],
                source=result["source"],
                width=result["width"],
                height=result["height"],
                size=result["size"],
                downloads=result.get("downloads"),
                likes=result.get("likes"),
                user=result.get("user"),
                tags=result.get("tags", [])
            ))
        
        processing_time = time.time() - start_time
        
        return ImageSearchResponse(
            caption=caption,
            similar_images=similar_images,
            total_found=search_results["total_found"],
            processing_time=processing_time
        )
        
    except Exception as e:
        logger.error(f"Error searching by image: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to search images: {str(e)}"
        )

@router.get("/health")
def search_health():
    """Check if search service is healthy"""
    return {
        "status": "healthy", 
        "service": "pixabay_image_search",
        "features": ["image_to_caption_to_search"],
        "api": "pixabay (free)",
        "quota": "20,000 requests/month"
    }
