import easyocr
import io
from PIL import Image
import numpy as np
import logging
from typing import List, Dict

logger = logging.getLogger(__name__)

# Global OCR reader
reader = None

def load_ocr_reader():
    global reader
    try:
        logger.info("Loading EasyOCR reader...")
        reader = easyocr.Reader(['en'])
        logger.info("EasyOCR reader loaded successfully")
    except Exception as e:
        logger.error(f"Failed to load EasyOCR reader: {e}")
        raise


try:
    load_ocr_reader()
except Exception as e:
    logger.warning(f"Could not load OCR reader at startup: {e}")

async def extract_text_from_image(file) -> List[Dict]:
    """Extract text from uploaded image using OCR"""
    global reader
    
    if reader is None:
        try:
            load_ocr_reader()
        except Exception as e:
            logger.error(f"Failed to load OCR reader: {e}")
            raise Exception("OCR reader not available")
    
    try:
        # Read image data
        contents = await file.read()
        image = Image.open(io.BytesIO(contents)).convert("RGB")
        
        # Convert PIL image to numpy array
        image_array = np.array(image)
        
        # Perform OCR
        results = reader.readtext(image_array)
        
        # Format results
        extracted_texts = []
        for (bbox, text, confidence) in results:
            extracted_texts.append({
                "text": text,
                "confidence": float(confidence),
                "bbox": bbox
            })
        
        logger.info(f"Extracted {len(extracted_texts)} text blocks")
        return extracted_texts
        
    except Exception as e:
        logger.error(f"Error extracting text from image: {e}")
        raise Exception(f"Failed to extract text: {str(e)}")
    finally:
        # Reset file pointer
        await file.seek(0)

def get_all_text(ocr_results: List[Dict]) -> str:
    """Combine all extracted text into a single string"""
    return " ".join([result["text"] for result in ocr_results])

def filter_by_confidence(ocr_results: List[Dict], min_confidence: float = 0.5) -> List[Dict]:
    """Filter OCR results by minimum confidence threshold"""
    return [result for result in ocr_results if result["confidence"] >= min_confidence]