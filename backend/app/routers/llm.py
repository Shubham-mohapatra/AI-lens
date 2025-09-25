from fastapi import APIRouter, HTTPException, Query
import time
import logging
from app.services.llm_service import generate_summary, enhance_caption_context
from app.models import LLMSummaryRequest, LLMSummaryResponse

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/summary", response_model=LLMSummaryResponse)
async def llm_summary(request: LLMSummaryRequest):
    """Generate enhanced summary from image caption using Google Gemini"""
    start_time = time.time()
    
    if not request.caption.strip():
        raise HTTPException(
            status_code=400,
            detail="Caption cannot be empty"
        )
    
    try:
        summary = await generate_summary(
            caption=request.caption,
            max_length=request.max_length,
            style=request.style
        )
        
        processing_time = time.time() - start_time
        
        return LLMSummaryResponse(
            summary=summary,
            original_caption=request.caption,
            processing_time=processing_time
        )
        
    except Exception as e:
        logger.error(f"Error generating summary: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate summary: {str(e)}"
        )

@router.post("/enhance-caption")
async def enhance_image_caption(
    caption: str = Query(..., description="Original image caption to enhance"),
    max_length: int = Query(50, description="Maximum length of enhanced caption")
):
    """Enhance image caption for better search context using Gemini AI"""
    start_time = time.time()
    
    if not caption.strip():
        raise HTTPException(
            status_code=400,
            detail="Caption cannot be empty"
        )
    
    try:
        enhanced_caption = await enhance_caption_context(caption)
        processing_time = time.time() - start_time
        
        return {
            "original_caption": caption,
            "enhanced_caption": enhanced_caption,
            "processing_time": processing_time,
            "improvement": "Enhanced for better search context and product discovery"
        }
        
    except Exception as e:
        logger.error(f"Error enhancing caption: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to enhance caption: {str(e)}"
        )

@router.post("/contextual-summary")
async def generate_contextual_summary(
    caption: str = Query(..., description="Image caption"),
    context_type: str = Query("general", description="Context type: fashion, food, nature, technology, general"),
    max_length: int = Query(150, description="Maximum summary length")
):
    """Generate context-aware summary based on image content type"""
    start_time = time.time()
    
    if not caption.strip():
        raise HTTPException(
            status_code=400,
            detail="Caption cannot be empty"
        )
    
    # Map context types to appropriate styles
    style_mapping = {
        "fashion": "creative",
        "food": "descriptive", 
        "nature": "descriptive",
        "technology": "technical",
        "general": "descriptive"
    }
    
    style = style_mapping.get(context_type, "descriptive")
    
    try:
        summary = await generate_summary(
            caption=caption,
            max_length=max_length,
            style=style
        )
        
        processing_time = time.time() - start_time
        
        return {
            "summary": summary,
            "original_caption": caption,
            "context_type": context_type,
            "style_used": style,
            "processing_time": processing_time
        }
        
    except Exception as e:
        logger.error(f"Error generating contextual summary: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate contextual summary: {str(e)}"
        )

@router.get("/health")
def llm_health():
    """Check if LLM service is healthy"""
    return {
        "status": "healthy", 
        "service": "llm_processing",
        "features": [
            "summary_generation",
            "caption_enhancement", 
            "contextual_analysis"
        ],
        "ai_provider": "Google Gemini (with fallback)"
    }
