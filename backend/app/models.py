from pydantic import BaseModel
from typing import List, Optional, Dict, Any, Union
from enum import Enum

class ImageFormat(str, Enum):
    JPEG = "image/jpeg"
    PNG = "image/png"
    WEBP = "image/webp"
    GIF = "image/gif"

class LLMStyle(str, Enum):
    DESCRIPTIVE = "descriptive"
    TECHNICAL = "technical" 
    CREATIVE = "creative"
    CONCISE = "concise"

class AnalysisType(str, Enum):
    QUICK = "quick"
    COMPREHENSIVE = "comprehensive"
    SMART_SEARCH = "smart_search"
    BATCH = "batch"

# Visual Intelligence Models
class ObjectDetection(BaseModel):
    name: str
    confidence: float
    description: str
    category: str
    bbox: Optional[Dict[str, float]] = None

class ObjectAnalysisResult(BaseModel):
    objects_found: int
    objects: List[ObjectDetection]
    method: str = "description_based"

class TextExtractionResult(BaseModel):
    text_found: bool
    extracted_text: str
    languages_detected: List[str]
    text_blocks: List[Dict[str, Any]] = []
    confidence: float
    note: Optional[str] = None

class TranslationResult(BaseModel):
    original_text: str
    translated_text: str
    source_language: str
    target_language: str
    confidence: float
    note: Optional[str] = None

class ShoppingProduct(BaseModel):
    title: str
    image: str
    source: str
    estimated_price: str
    buy_links: List[str]
    rating: Optional[float] = None
    reviews: Optional[int] = None

class ShoppingResult(BaseModel):
    products_found: int
    products: List[ShoppingProduct]
    search_query: str
    note: Optional[str] = None

class LandmarkInfo(BaseModel):
    name: str
    description: str
    confidence: float
    location: str
    type: str
    historical_info: Optional[str] = None

class LandmarkResult(BaseModel):
    landmark_detected: bool
    possible_landmarks: List[LandmarkInfo]

class NatureIdentification(BaseModel):
    type: str  # "plants" or "animals"
    name: str
    confidence: float
    scientific_name: str
    description: str
    care_tips: Optional[str] = None
    habitat: Optional[str] = None

class NatureResult(BaseModel):
    nature_found: bool
    identified: List[NatureIdentification]
    note: Optional[str] = None

class FoodNutrition(BaseModel):
    calories: str
    protein: str
    carbs: str
    fat: str
    fiber: Optional[str] = None

class DietaryInfo(BaseModel):
    vegetarian: str
    vegan: str
    gluten_free: str
    dairy_free: Optional[str] = None

class FoodInfo(BaseModel):
    name: str
    estimated_calories: str
    main_ingredients: List[str]
    cuisine_type: str
    dietary_info: DietaryInfo

class FoodResult(BaseModel):
    food_detected: bool
    dish_info: Optional[FoodInfo] = None
    nutrition: Optional[FoodNutrition] = None
    note: Optional[str] = None

class QRCode(BaseModel):
    type: str = "QR"
    content: str
    format: str

class Barcode(BaseModel):
    type: str = "barcode"
    content: str
    format: str
    product_info: Optional[Dict[str, str]] = None

class CodeScanResult(BaseModel):
    codes_found: int
    qr_codes: List[QRCode] = []
    barcodes: List[Barcode] = []
    note: Optional[str] = None

class BasicImageInfo(BaseModel):
    description: str
    confidence: float
    categories: List[str]

class VisualIntelligenceResults(BaseModel):
    basic_info: BasicImageInfo
    objects: ObjectAnalysisResult
    text: TextExtractionResult
    shopping: ShoppingResult
    translation: Optional[TranslationResult] = None
    landmarks: LandmarkResult
    nature: NatureResult
    food: FoodResult
    codes: CodeScanResult

class ImageMetadata(BaseModel):
    filename: str
    size: int
    content_type: str

class AnalysisFeatures(BaseModel):
    objects: bool = True
    text: bool = True
    shopping: bool = True
    translation: bool = False
    landmarks: bool = False
    nature: bool = False
    food: bool = False

class AnalysisMeta(BaseModel):
    processing_time: float
    image_info: ImageMetadata
    features_used: AnalysisFeatures

class VisualIntelligenceResponse(BaseModel):
    analysis_results: VisualIntelligenceResults
    meta: AnalysisMeta

# Search Models
class SmartSearchResult(BaseModel):
    search_results: Dict[str, Any]
    detected_type: str
    original_description: str
    processing_time: Optional[float] = None

# Batch Processing Models
class BatchAnalysisItem(BaseModel):
    index: int
    filename: str
    caption: Optional[str] = None
    similar_images: Optional[List[Dict[str, Any]]] = None
    success: bool
    error: Optional[str] = None

class BatchAnalysisResponse(BaseModel):
    total_files: int
    processed: int
    failed: int
    results: List[BatchAnalysisItem]
    processing_time: float

# Comparison Models
class ImageComparison(BaseModel):
    captions: Optional[Dict[str, str]] = None
    text_similarity: Optional[float] = None
    size_comparison: Dict[str, Any]
    format_info: Dict[str, Any]

class ComparisonResponse(BaseModel):
    comparison_results: ImageComparison
    processing_time: float
    images_compared: Dict[str, str]

class DuplicateInfo(BaseModel):
    image1: Dict[str, Any]
    image2: Dict[str, Any]
    similarity_score: float

class DuplicateDetectionResponse(BaseModel):
    total_images_processed: int
    potential_duplicates_found: int
    duplicates: List[DuplicateInfo]
    similarity_threshold: float
    processing_time: float

# Legacy Models (keeping for compatibility)
class ImageAnalysisResponse(BaseModel):
    caption: str
    confidence: Optional[float] = None
    processing_time: Optional[float] = None
    cached: bool = False

class ImageSearchResult(BaseModel):
    url: str
    thumbnail: str
    title: str
    source: str
    width: int
    height: int
    size: str
    downloads: Optional[int] = None
    likes: Optional[int] = None
    user: Optional[str] = None
    tags: List[str] = []

class ImageSearchResponse(BaseModel):
    caption: str
    similar_images: List[ImageSearchResult]
    total_found: int
    processing_time: Optional[float] = None
    cached: bool = False
    api_used: str = "pixabay"

class SearchResponse(BaseModel):
    results: List[str]
    query_type: str
    total_results: int
    processing_time: Optional[float] = None

class BingImageResult(BaseModel):
    url: str
    thumbnail: str
    title: str
    source: str
    width: int
    height: int
    size: str
    encoding: str

class BingSearchResponse(BaseModel):
    query: str
    original_description: Optional[str] = None
    results: List[BingImageResult]
    total_found: int
    processing_time: Optional[float] = None

class LLMSummaryRequest(BaseModel):
    caption: str
    max_length: Optional[int] = 150
    style: Optional[str] = "descriptive"

class LLMSummaryResponse(BaseModel):
    summary: str
    original_caption: str
    processing_time: Optional[float] = None

class ErrorResponse(BaseModel):
    error: str
    detail: Optional[str] = None
    timestamp: Optional[str] = None

class HealthResponse(BaseModel):
    status: str
    service: str
    features: Optional[List[str]] = None
    version: Optional[str] = None