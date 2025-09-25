from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
import time
import logging
from app.services.caption import generate_caption
from app.models import ImageAnalysisResponse, ErrorResponse

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/caption", response_model=ImageAnalysisResponse)
async def analyze_image(file: UploadFile = File(...)):
    """Generate caption for uploaded image"""
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
        caption = await generate_caption(file)
        processing_time = time.time() - start_time
        
        return ImageAnalysisResponse(
            caption=caption,
            processing_time=processing_time
        )
        
    except Exception as e:
        logger.error(f"Error analyzing image: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to analyze image: {str(e)}"
        )

@router.get("/health")
def analyze_health():
    """Check if image analysis service is healthy"""
    return {"status": "healthy", "service": "image_analysis"}
