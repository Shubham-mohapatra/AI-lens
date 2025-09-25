
from fastapi import APIRouter, UploadFile, File, HTTPException, Query
from typing import Dict, List, Optional, Any
import time
import logging
import asyncio
from app.services.caption import generate_caption
from app.services.pixabay_search import search_similar_images_pixabay
from app.cache import cache, cache_key_from_image

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/analyze")
async def visual_intelligence_analyze(
    file: UploadFile = File(...),
    include_objects: bool = Query(True, description="Detect and identify objects"),
    include_text: bool = Query(True, description="Extract and recognize text"),
    include_shopping: bool = Query(True, description="Find similar products to buy"),
    include_translation: bool = Query(False, description="Translate detected text"),
    target_language: str = Query("en", description="Target language for translation"),
    include_landmarks: bool = Query(False, description="Identify landmarks and places"),
    include_nature: bool = Query(False, description="Identify plants and animals"),
    include_food: bool = Query(False, description="Analyze food and nutrition"),
    confidence_threshold: float = Query(0.5, ge=0.1, le=1.0)
):
    """
    Apple Visual Intelligence style comprehensive image analysis
    """
    start_time = time.time()
    
    # Validate file
    if not file.content_type.startswith("image/"):
        raise HTTPException(
            status_code=400,
            detail="File must be an image"
        )
    
    if file.size and file.size > 15 * 1024 * 1024:  # 15MB limit
        raise HTTPException(
            status_code=400,
            detail="File size must be less than 15MB"
        )
    
    try:
        # Check cache first
        cache_key = cache_key_from_image(await file.read(), {
            "objects": include_objects,
            "text": include_text,
            "shopping": include_shopping
        })
        await file.seek(0)
        
        cached_result = cache.get(cache_key)
        if cached_result:
            logger.info("Returning cached visual intelligence result")
            return cached_result
        
        # Initialize results structure
        results = {
            "basic_info": {},
            "objects": {},
            "text": {},
            "shopping": {},
            "translation": {},
            "landmarks": {},
            "nature": {},
            "food": {},
            "codes": {}
        }
        
        # Basic image description (always included)
        logger.info(" Generating image description...")
        description = await generate_caption(file)
        results["basic_info"] = {
            "description": description,
            "confidence": 0.85,
            "categories": await categorize_image_content(description)
        }
        
        # Object detection and recognition
        if include_objects:
            logger.info(" Detecting objects...")
            results["objects"] = await detect_and_identify_objects(file, confidence_threshold)
        
        # Text extraction and OCR
        if include_text:
            logger.info(" Extracting text...")
            results["text"] = await extract_and_analyze_text(file)
            
            # Translation if requested
            if include_translation and results["text"].get("extracted_text"):
                logger.info(f" Translating to {target_language}...")
                results["translation"] = await translate_text(
                    results["text"]["extracted_text"], 
                    target_language
                )
        
        # Visual shopping - find similar products
        if include_shopping:
            logger.info(" Finding similar products...")
            results["shopping"] = await find_similar_products(description)
        
        # Landmark recognition
        if include_landmarks:
            logger.info(" Identifying landmarks...")
            results["landmarks"] = await identify_landmarks(file, description)
        
        # Nature identification (plants, animals)
        if include_nature:
            logger.info(" Identifying nature...")
            results["nature"] = await identify_nature(file, description)
        
        # Food recognition and nutrition
        if include_food:
            logger.info(" Analyzing food...")
            results["food"] = await analyze_food(file, description)
        
        # QR codes and barcodes
        logger.info("📱 Scanning codes...")
        results["codes"] = await scan_codes(file)
        
        processing_time = time.time() - start_time
        
        response = {
            "analysis_results": results,
            "meta": {
                "processing_time": processing_time,
                "image_info": {
                    "filename": file.filename,
                    "size": file.size,
                    "content_type": file.content_type
                },
                "features_used": {
                    "objects": include_objects,
                    "text": include_text,
                    "shopping": include_shopping,
                    "translation": include_translation,
                    "landmarks": include_landmarks,
                    "nature": include_nature,
                    "food": include_food
                }
            }
        }
        
        # Cache the result
        cache.set(cache_key, response, ttl=3600)  # 1 hour
        
        return response
        
    except Exception as e:
        logger.error(f"Visual intelligence analysis failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Analysis failed: {str(e)}"
        )

@router.post("/quick-scan")
async def quick_visual_scan(file: UploadFile = File(...)):
    """Quick scan for immediate results - like Camera Control"""
    return await visual_intelligence_analyze(
        file=file,
        include_objects=True,
        include_text=True,
        include_shopping=False,
        include_translation=False,
        include_landmarks=False,
        include_nature=False,
        include_food=False,
        confidence_threshold=0.7
    )

@router.post("/smart-search")
async def smart_visual_search(
    file: UploadFile = File(...),
    search_type: str = Query("general", description="Type: general, shopping, food, nature, landmarks")
):
    """Smart contextual search based on image content"""
    try:
        # Generate description
        description = await generate_caption(file)
        
        # Generate contextual query for better results
        contextual_query = await generate_contextual_search_query(description)
        
        # Determine search strategy based on content with better context understanding
        if any(word in description.lower() for word in ["food", "dish", "meal", "restaurant", "cuisine"]):
            search_type = "food"
        elif any(word in description.lower() for word in ["plant", "flower", "tree", "nature", "garden"]):
            search_type = "nature"
        elif any(word in description.lower() for word in ["building", "architecture", "landmark", "monument"]):
            search_type = "landmarks"
        elif any(word in description.lower() for word in ["clothing", "fashion", "wear", "outfit", "style", "man", "woman"]):
            search_type = "shopping"
        elif any(word in description.lower() for word in ["product", "item", "device", "gadget", "tool"]):
            search_type = "shopping"
        
        # Enhanced search based on type
        if search_type == "shopping":
            results = await find_similar_products(description)
        elif search_type == "food":
            results = await analyze_food(file, description)
        elif search_type == "nature":
            results = await identify_nature(file, description)
        elif search_type == "landmarks":
            results = await identify_landmarks(file, description)
        else:
            # General search with contextual enhancement
            search_results = await search_similar_images_pixabay(contextual_query, count=8)
            results = {
                "search_type": "general",
                "description": description,
                "contextual_query": contextual_query,
                "similar_images": search_results
            }
        
        return {
            "search_results": results,
            "detected_type": search_type,
            "original_description": description,
            "contextual_understanding": contextual_query
        }
        
    except Exception as e:
        logger.error(f"Smart search failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Smart search failed: {str(e)}"
        )

# Helper functions for different analysis types

async def categorize_image_content(description: str) -> List[str]:
    """Categorize image content like Apple's system with enhanced fashion understanding"""
    categories = []
    desc_lower = description.lower()
    
    category_keywords = {
        "fashion": ["fashion", "style", "outfit", "clothing", "wear", "sweater", "hoodie", "pants", "trousers", "jeans", "shirt", "dress", "skirt", "jacket", "coat"],
        "menswear": ["man", "male", "guy", "men's", "masculine", "gentleman"],
        "womenswear": ["woman", "female", "lady", "women's", "feminine"],
        "footwear": ["shoes", "sneakers", "boots", "sandals", "heels", "footwear"],
        "accessories": ["watch", "bag", "jewelry", "hat", "sunglasses", "belt"],
        "lifestyle": ["casual", "professional", "formal", "street", "urban", "minimal", "elegant"],
        "people": ["person", "people", "portrait", "face", "individual"],
        "animals": ["dog", "cat", "bird", "animal", "pet", "wildlife"],
        "food": ["food", "dish", "meal", "restaurant", "cooking", "kitchen", "cuisine", "dining"],
        "nature": ["tree", "flower", "plant", "garden", "landscape", "outdoor", "forest", "mountain"],
        "technology": ["phone", "computer", "device", "electronic", "screen", "laptop", "smartphone"],
        "transportation": ["car", "bike", "train", "bus", "vehicle", "motorcycle"],
        "architecture": ["building", "house", "architecture", "structure", "interior", "room"],
        "shopping": ["product", "item", "store", "brand", "commercial"],
        "documents": ["text", "document", "paper", "book", "sign", "writing"],
        "sports": ["sport", "fitness", "gym", "exercise", "athletic", "workout"],
        "art": ["art", "painting", "creative", "design", "gallery", "artistic"]
    }
    
    for category, keywords in category_keywords.items():
        if any(keyword in desc_lower for keyword in keywords):
            categories.append(category)
    
    # Special fashion context detection
    if any(cat in categories for cat in ["menswear", "womenswear", "footwear", "accessories"]):
        if "fashion" not in categories:
            categories.append("fashion")
    
    # If we detect a person wearing something, add lifestyle
    if "people" in categories and any(cat in categories for cat in ["fashion", "menswear", "womenswear"]):
        categories.append("lifestyle")
    
    return categories if categories else ["general"]

async def detect_and_identify_objects(file: UploadFile, confidence_threshold: float) -> Dict[str, Any]:
    """Enhanced object detection using real YOLOv8"""
    try:
        # Try to use the real YOLO detector from detect.py
        try:
            from app.services.detect import detect_objects
            logger.info("Using YOLOv8 for object detection")
            
            # Get YOLO detections
            detections = await detect_objects(file, confidence_threshold)
            
            # Format for Visual Intelligence response
            objects = []
            for detection in detections:
                objects.append({
                    "name": detection["class"],
                    "confidence": detection["confidence"],
                    "description": f"{detection['class'].capitalize()} detected with {detection['confidence']:.1%} confidence",
                    "category": "object",
                    "bbox": detection.get("bbox")
                })
            
            return {
                "objects_found": len(objects),
                "objects": objects,
                "method": "yolov8",
                "confidence_threshold": confidence_threshold
            }
            
        except Exception as yolo_error:
            logger.warning(f"YOLOv8 not available, using description-based detection: {yolo_error}")
            # Fallback to description-based detection
            return await detect_objects_from_description(file, confidence_threshold)
            
    except Exception as e:
        logger.error(f"Object detection failed: {e}")
        return {"objects_found": 0, "objects": [], "error": str(e), "method": "failed"}

async def detect_objects_from_description(file: UploadFile, confidence_threshold: float) -> Dict[str, Any]:
    """Fallback object detection using image description"""
    try:
        description = await generate_caption(file)
        
        # Enhanced object detection from description
        common_objects = {
            # People
            "person": ["person", "man", "woman", "child", "people", "individual"],
            "face": ["face", "portrait", "head"],
            
            # Clothing & Fashion
            "clothing": ["clothing", "shirt", "jacket", "dress", "pants", "sweater"],
            "shoes": ["shoes", "sneakers", "boots", "footwear"],
            "accessories": ["watch", "bag", "hat", "jewelry"],
            
            # Technology
            "phone": ["phone", "smartphone", "mobile"],
            "computer": ["computer", "laptop", "screen", "monitor"],
            "device": ["device", "electronic", "gadget"],
            
            # Furniture & Objects
            "chair": ["chair", "seat"],
            "table": ["table", "desk"],
            "book": ["book", "document", "paper"],
            "bottle": ["bottle", "container"],
            "cup": ["cup", "mug", "glass"],
            
            # Food
            "food": ["food", "meal", "dish", "plate"],
            
            # Vehicles
            "car": ["car", "vehicle", "automobile"],
            "bike": ["bike", "bicycle", "motorcycle"],
            
            # Nature
            "tree": ["tree", "plant", "vegetation"],
            "flower": ["flower", "bloom", "blossom"],
            
            # Buildings
            "building": ["building", "house", "structure", "architecture"],
            "sign": ["sign", "text", "writing"]
        }
        
        detected_objects = []
        desc_words = description.lower().split()
        
        for obj_name, keywords in common_objects.items():
            for keyword in keywords:
                if keyword in description.lower():
                    # Calculate confidence based on how specific the match is
                    base_confidence = confidence_threshold + 0.1
                    if keyword in desc_words:  # Exact word match
                        base_confidence += 0.2
                    if keyword == obj_name:  # Exact object name
                        base_confidence += 0.1
                    
                    # Don't exceed 0.95 confidence
                    final_confidence = min(base_confidence, 0.95)
                    
                    detected_objects.append({
                        "name": obj_name,
                        "confidence": final_confidence,
                        "description": f"{obj_name.capitalize()} detected from image description",
                        "category": categorize_object(obj_name),
                        "detected_via": keyword
                    })
                    break  # Only add each object once
        
        return {
            "objects_found": len(detected_objects),
            "objects": detected_objects,
            "method": "description_based",
            "source_description": description
        }
    except Exception as e:
        logger.error(f"Description-based object detection failed: {e}")
        return {"objects_found": 0, "objects": [], "error": str(e)}

def categorize_object(obj_name: str) -> str:
    """Categorize detected objects"""
    categories = {
        "person": "people",
        "face": "people",
        "clothing": "fashion",
        "shoes": "fashion",
        "accessories": "fashion",
        "phone": "technology",
        "computer": "technology",
        "device": "technology",
        "chair": "furniture",
        "table": "furniture",
        "book": "items",
        "bottle": "items",
        "cup": "items",
        "food": "food",
        "car": "transportation",
        "bike": "transportation",
        "tree": "nature",
        "flower": "nature",
        "building": "architecture",
        "sign": "text"
    }
    return categories.get(obj_name, "object")

async def extract_and_analyze_text(file: UploadFile) -> Dict[str, Any]:
    """Extract and analyze text from images"""
    try:
        # Placeholder for OCR implementation
        # In real implementation, use EasyOCR or Tesseract
        return {
            "text_found": False,
            "extracted_text": "",
            "languages_detected": ["en"],
            "text_blocks": [],
            "confidence": 0.0,
            "note": "OCR implementation needed - install EasyOCR or Tesseract"
        }
    except Exception as e:
        return {"text_found": False, "error": str(e)}

async def translate_text(text: str, target_language: str) -> Dict[str, Any]:
    """Translate extracted text"""
    try:
        # Placeholder for translation
        # In real implementation, use Google Translate API or similar
        return {
            "original_text": text,
            "translated_text": text,  # Would be actual translation
            "source_language": "en",
            "target_language": target_language,
            "confidence": 0.0,
            "note": "Translation API needed - Google Translate, DeepL, etc."
        }
    except Exception as e:
        return {"translated": False, "error": str(e)}

async def generate_contextual_search_query(description: str) -> str:
    """Generate contextual search queries that understand broader concepts"""
    desc_lower = description.lower()
    
    # Fashion & Clothing Context
    if any(word in desc_lower for word in ["sweater", "hoodie", "pullover", "jumper", "cardigan"]):
        if any(word in desc_lower for word in ["black", "dark", "minimal", "casual"]):
            return "minimalist casual menswear black sweater"
        return "casual sweater menswear fashion"
    
    if any(word in desc_lower for word in ["pants", "trousers", "jeans", "chinos"]):
        if "white" in desc_lower or "cream" in desc_lower or "beige" in desc_lower:
            return "casual white pants menswear minimalist"
        return "casual pants menswear fashion"
        
    if any(word in desc_lower for word in ["man", "male", "guy"]) and any(word in desc_lower for word in ["standing", "wearing", "outfit"]):
        style_indicators = []
        if any(word in desc_lower for word in ["minimal", "simple", "clean", "basic"]):
            style_indicators.append("minimalist")
        if any(word in desc_lower for word in ["casual", "relaxed", "comfortable"]):
            style_indicators.append("casual")
        if any(word in desc_lower for word in ["street", "urban", "modern"]):
            style_indicators.append("streetwear")
        if any(word in desc_lower for word in ["professional", "business", "formal"]):
            style_indicators.append("formal")
            
        base_query = "menswear fashion style"
        if style_indicators:
            return f"{' '.join(style_indicators)} {base_query}"
        return f"casual {base_query}"
    
    # Technology Context
    if any(word in desc_lower for word in ["phone", "smartphone", "mobile"]):
        if any(brand in desc_lower for brand in ["iphone", "apple", "samsung", "android"]):
            return "modern smartphone technology mobile device"
        return "smartphone mobile phone technology"
    
    if any(word in desc_lower for word in ["laptop", "computer", "macbook"]):
        return "modern laptop computer technology workspace"
    
    # Food & Cuisine Context
    if any(word in desc_lower for word in ["pizza", "burger", "sandwich"]):
        return "delicious food cuisine restaurant dining"
    
    if any(word in desc_lower for word in ["coffee", "latte", "cappuccino"]):
        return "coffee cafe barista lifestyle"
    
    # Footwear Context
    if any(word in desc_lower for word in ["shoes", "sneakers", "boots", "sandals"]):
        if any(brand in desc_lower for brand in ["nike", "adidas", "converse", "vans"]):
            brand_found = next(brand for brand in ["nike", "adidas", "converse", "vans"] if brand in desc_lower)
            return f"{brand_found} footwear sneakers style fashion"
        return "footwear shoes fashion style"
    
    # Home & Lifestyle Context
    if any(word in desc_lower for word in ["room", "interior", "furniture", "decor"]):
        return "home decor interior design lifestyle"
    
    # Nature & Outdoor Context
    if any(word in desc_lower for word in ["landscape", "mountain", "forest", "beach"]):
        return "nature outdoor landscape photography travel"
    
    # Sports & Fitness Context
    if any(word in desc_lower for word in ["gym", "workout", "fitness", "exercise"]):
        return "fitness workout health lifestyle sports"
    
    # Art & Culture Context
    if any(word in desc_lower for word in ["painting", "art", "gallery", "museum"]):
        return "art culture creative design inspiration"
    
    # Default contextual enhancement
    # Remove very specific details and focus on broader concepts
    words_to_remove = ["'s", "women", "men", "2", "air", "zoom", "size", "color"]
    filtered_words = []
    for word in desc_lower.split():
        if not any(remove_word in word for remove_word in words_to_remove):
            filtered_words.append(word)
    
    # If we have brand names, keep them but make query more general
    brands = ["nike", "adidas", "apple", "samsung", "sony", "canon", "bmw", "mercedes"]
    found_brand = next((brand for brand in brands if brand in desc_lower), None)
    
    if found_brand:
        category = "fashion" if any(word in desc_lower for word in ["shoe", "clothing", "wear"]) else "product"
        return f"{found_brand} {category} style lifestyle"
    
    # Fallback: use first few meaningful words
    meaningful_words = [word for word in filtered_words if len(word) > 3][:3]
    return " ".join(meaningful_words) if meaningful_words else description

async def find_similar_products(description: str) -> Dict[str, Any]:
    """Find similar products for shopping with contextual understanding"""
    try:
        # Enhanced contextual search queries
        contextual_query = await generate_contextual_search_query(description)
        
        # Use the contextual query for better results
        results = await search_similar_images_pixabay(contextual_query, count=6)
        
        return {
            "products_found": len(results),
            "products": [
                {
                    "title": result.get("title", "Product"),
                    "image": result.get("url", ""),
                    "source": "pixabay",
                    "estimated_price": "Price varies",
                    "buy_links": ["Amazon", "eBay", "Google Shopping"]
                }
                for result in results
            ],
            "search_query": contextual_query,
            "original_description": description,
            "note": "Enhanced contextual search for better product discovery"
        }
    except Exception as e:
        return {"products_found": 0, "error": str(e)}

async def identify_landmarks(file: UploadFile, description: str) -> Dict[str, Any]:
    """Identify landmarks and places"""
    try:
        landmark_keywords = ["building", "architecture", "monument", "landmark", "structure", "tower", "bridge"]
        
        if any(keyword in description.lower() for keyword in landmark_keywords):
            return {
                "landmark_detected": True,
                "possible_landmarks": [
                    {
                        "name": "Architectural Structure",
                        "description": description,
                        "confidence": 0.6,
                        "location": "Unknown",
                        "type": "building"
                    }
                ],
                "note": "Landmark recognition API needed - Google Places, etc."
            }
        
        return {
            "landmark_detected": False,
            "possible_landmarks": []
        }
    except Exception as e:
        return {"landmark_detected": False, "error": str(e)}

async def identify_nature(file: UploadFile, description: str) -> Dict[str, Any]:
    """Identify plants and animals"""
    try:
        nature_keywords = {
            "plants": ["flower", "tree", "plant", "leaf", "garden", "botanical"],
            "animals": ["dog", "cat", "bird", "animal", "wildlife", "pet"]
        }
        
        identified = []
        desc_lower = description.lower()
        
        for category, keywords in nature_keywords.items():
            for keyword in keywords:
                if keyword in desc_lower:
                    identified.append({
                        "type": category,
                        "name": keyword.capitalize(),
                        "confidence": 0.7,
                        "scientific_name": "Unknown",
                        "description": f"{keyword.capitalize()} identified in image",
                        "care_tips": "Consult gardening/pet care resources"
                    })
                    break
        
        return {
            "nature_found": len(identified) > 0,
            "identified": identified,
            "note": "PlantNet or iNaturalist API integration recommended"
        }
    except Exception as e:
        return {"nature_found": False, "error": str(e)}

async def analyze_food(file: UploadFile, description: str) -> Dict[str, Any]:
    """Analyze food and provide nutrition info"""
    try:
        food_keywords = ["food", "dish", "meal", "plate", "cooking", "restaurant", "cuisine"]
        
        if any(keyword in description.lower() for keyword in food_keywords):
            return {
                "food_detected": True,
                "dish_info": {
                    "name": description,
                    "estimated_calories": "Unknown",
                    "main_ingredients": ["Unknown"],
                    "cuisine_type": "Unknown",
                    "dietary_info": {
                        "vegetarian": "Unknown",
                        "vegan": "Unknown",
                        "gluten_free": "Unknown"
                    }
                },
                "nutrition": {
                    "calories": "N/A",
                    "protein": "N/A",
                    "carbs": "N/A",
                    "fat": "N/A"
                },
                "note": "Food recognition API needed - Clarifai Food, Spoonacular, etc."
            }
        
        return {
            "food_detected": False,
            "dish_info": {}
        }
    except Exception as e:
        return {"food_detected": False, "error": str(e)}

async def scan_codes(file: UploadFile) -> Dict[str, Any]:
    """Scan QR codes and barcodes"""
    try:
        # Placeholder for code scanning
        # In real implementation, use pyzbar or OpenCV
        return {
            "codes_found": 0,
            "qr_codes": [],
            "barcodes": [],
            "note": "QR/Barcode scanning library needed - pyzbar, OpenCV"
        }
    except Exception as e:
        return {"codes_found": 0, "error": str(e)}

@router.get("/health")
def visual_intelligence_health():
    """Health check for Visual Intelligence service"""
    return {
        "status": "healthy",
        "service": "visual_intelligence",
        "features": [
            "comprehensive_analysis",
            "smart_search",
            "quick_scan",
            "object_detection",
            "text_recognition",
            "shopping_integration",
            "nature_identification",
            "food_analysis",
            "landmark_recognition",
            "code_scanning"
        ],
        "inspiration": "Apple Visual Intelligence",
        "note": "Some features need additional API integrations for full functionality"
    }