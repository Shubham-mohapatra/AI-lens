"""
Batch processing router for handling multiple images at once
"""
from fastapi import APIRouter, UploadFile, File, HTTPException, BackgroundTasks
from typing import List, Dict, Any
import asyncio
import time
import logging
from app.services.caption import generate_caption
from app.services.pixabay_search import search_by_image_description
from app.models import ImageSearchResponse, ImageSearchResult

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/analyze-multiple")
async def analyze_multiple_images(
    files: List[UploadFile] = File(...),
    max_files: int = 10
):
    """Analyze multiple images simultaneously"""
    if len(files) > max_files:
        raise HTTPException(
            status_code=400,
            detail=f"Too many files. Maximum {max_files} files allowed"
        )
    
    start_time = time.time()
    results = []
    
    # Process all files concurrently
    tasks = []
    for i, file in enumerate(files):
        # Validate file
        if not file.content_type.startswith("image/"):
            results.append({
                "index": i,
                "filename": file.filename,
                "error": "Invalid file type",
                "success": False
            })
            continue
        
        # Add to processing tasks
        tasks.append(process_single_image(file, i))
    
    # Wait for all tasks to complete
    if tasks:
        batch_results = await asyncio.gather(*tasks, return_exceptions=True)
        
        for result in batch_results:
            if isinstance(result, Exception):
                results.append({
                    "error": str(result),
                    "success": False
                })
            else:
                results.append(result)
    
    processing_time = time.time() - start_time
    
    return {
        "total_files": len(files),
        "processed": len([r for r in results if r.get("success", False)]),
        "failed": len([r for r in results if not r.get("success", True)]),
        "results": results,
        "processing_time": processing_time
    }

async def process_single_image(file: UploadFile, index: int) -> Dict[str, Any]:
    """Process a single image and return results"""
    try:
        # Generate caption
        caption = await generate_caption(file)
        
        return {
            "index": index,
            "filename": file.filename,
            "caption": caption,
            "success": True
        }
    except Exception as e:
        logger.error(f"Error processing image {index}: {e}")
        return {
            "index": index,
            "filename": file.filename,
            "error": str(e),
            "success": False
        }

@router.post("/search-multiple")
async def search_multiple_images(
    files: List[UploadFile] = File(...),
    results_per_image: int = 5,
    max_files: int = 5
):
    """Search for similar images for multiple uploaded images"""
    if len(files) > max_files:
        raise HTTPException(
            status_code=400,
            detail=f"Too many files. Maximum {max_files} files allowed for search"
        )
    
    start_time = time.time()
    results = []
    
    for i, file in enumerate(files):
        try:
            if not file.content_type.startswith("image/"):
                results.append({
                    "index": i,
                    "filename": file.filename,
                    "error": "Invalid file type",
                    "success": False
                })
                continue
            
            # Generate caption and search
            caption = await generate_caption(file)
            search_results = await search_by_image_description(caption, results_per_image)
            
            # Format results
            similar_images = []
            for result in search_results["results"]:
                similar_images.append({
                    "url": result["url"],
                    "thumbnail": result["thumbnail"],
                    "title": result["title"],
                    "source": result["source"]
                })
            
            results.append({
                "index": i,
                "filename": file.filename,
                "caption": caption,
                "similar_images": similar_images,
                "success": True
            })
            
        except Exception as e:
            logger.error(f"Error searching for image {i}: {e}")
            results.append({
                "index": i,
                "filename": file.filename,
                "error": str(e),
                "success": False
            })
    
    processing_time = time.time() - start_time
    
    return {
        "total_files": len(files),
        "processed": len([r for r in results if r.get("success", False)]),
        "results": results,
        "processing_time": processing_time
    }

@router.get("/health")
def batch_health():
    """Check if batch processing service is healthy"""
    return {
        "status": "healthy",
        "service": "batch_processing",
        "features": [
            "multiple_image_analysis",
            "batch_search",
            "concurrent_processing"
        ]
    }