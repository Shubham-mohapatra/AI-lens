from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging
import sys
import os

# Add the parent directory to Python path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.routers import analyze, search, llm, visual_intelligence, batch
from app.config import settings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info(" Starting AI Lens API...")
    logger.info(f" Version: {settings.app_version}")
    logger.info(f" Debug mode: {settings.debug}")
    logger.info("API is ready!")
    yield
    # Shutdown
    logger.info(" Shutting down AI Lens API...")

# Create FastAPI app
app = FastAPI(
    title=" AI Lens - Visual Intelligence API",
    description="Apple Visual Intelligence inspired AI-powered comprehensive image analysis system with BLIP captioning, Pixabay search, and advanced visual recognition",
    version=settings.app_version,
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=settings.allowed_methods,
    allow_headers=settings.allowed_headers,
)

# Include routers
app.include_router(visual_intelligence.router, prefix="/visual", tags=["🍎 Visual Intelligence"])
app.include_router(batch.router, prefix="/batch", tags=[" Batch Processing"])
app.include_router(analyze.router, prefix="/analyze", tags=[" Image Analysis"])
app.include_router(search.router, prefix="/search", tags=[" Image Search"])
app.include_router(llm.router, prefix="/llm", tags=[" LLM Services"])

@app.get("/")
def root():
    return {
        "message": " AI Lens - Visual Intelligence API",
        "inspiration": "Apple Visual Intelligence",
        "version": settings.app_version,
        "docs": "/docs",
        "features": {
            "visual_intelligence": " Comprehensive image analysis like Apple's system",
            "quick_scan": " Instant analysis for immediate results",
            "smart_search": " Contextual search based on image content",
            "batch_processing": " Analyze multiple images simultaneously", 
            "image_comparison": " Compare and find duplicate images",
            "shopping": " Find similar products to buy",
            "text_recognition": " Extract and translate text",
            "nature_id": " Identify plants and animals",
            "food_analysis": " Analyze food and nutrition",
            "landmark_recognition": " Identify landmarks and places"
        },
        "main_endpoints": {
            "visual_intelligence": "/visual/analyze",
            "quick_scan": "/visual/quick-scan",
            "smart_search": "/visual/smart-search",
            "batch_analysis": "/batch/analyze-multiple",
            "image_comparison": "/compare/compare",
            "health": "/health"
        }
    }

@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "message": "🍎 AI Lens Visual Intelligence is running",
        "version": settings.app_version,
        "inspiration": "Apple Visual Intelligence",
        "services": {
            "visual_intelligence": " Comprehensive analysis system",
            "caption": " BLIP image captioning",
            "search": " Pixabay API integrated",
            "batch": " Multi-image processing",
            "comparison": " Image similarity analysis",
            "llm": " Enhanced summaries"
        },
        "capabilities": [
            "Object Recognition",
            "Text Extraction & Translation", 
            "Visual Shopping",
            "Nature Identification",
            "Food Analysis",
            "Landmark Recognition",
            "QR/Barcode Scanning",
            "Smart Contextual Search"
        ]
    }