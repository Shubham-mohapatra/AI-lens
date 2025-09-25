import os
from PIL import Image
from transformers import BlipProcessor, BlipForConditionalGeneration
from dotenv import load_dotenv
import io
import logging

load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

HF_TOKEN = os.getenv("HUGGINGFACE_TOKEN")

# Global variables for model and processor
processor = None
model = None

def load_models():
    """Load BLIP models once at startup"""
    global processor, model
    try:
        logger.info("Loading BLIP models...")
        processor = BlipProcessor.from_pretrained(
            "Salesforce/blip-image-captioning-base",
            token=HF_TOKEN  # Updated from use_auth_token
        )
        model = BlipForConditionalGeneration.from_pretrained(
            "Salesforce/blip-image-captioning-base",
            token=HF_TOKEN  # Updated from use_auth_token
        )
        logger.info("BLIP models loaded successfully")
    except Exception as e:
        logger.error(f"Failed to load BLIP models: {e}")
        raise

# Load models at module import
try:
    load_models()
except Exception as e:
    logger.warning(f"Could not load models at startup: {e}")

async def generate_caption(file):
    """Generate caption for uploaded image"""
    global processor, model
    
    if processor is None or model is None:
        try:
            load_models()
        except Exception as e:
            logger.error(f"Failed to load models: {e}")
            raise Exception("Image captioning models not available")
    
    try:
        # Read image data
        contents = await file.read()
        image = Image.open(io.BytesIO(contents)).convert("RGB")
        
        # Generate caption
        inputs = processor(image, return_tensors="pt")
        output = model.generate(**inputs, max_length=50, num_beams=5)
        caption = processor.decode(output[0], skip_special_tokens=True)
        
        logger.info(f"Generated caption: {caption}")
        return caption
        
    except Exception as e:
        logger.error(f"Error generating caption: {e}")
        raise Exception(f"Failed to generate caption: {str(e)}")
    finally:
        # Reset file pointer for potential reuse
        await file.seek(0)
