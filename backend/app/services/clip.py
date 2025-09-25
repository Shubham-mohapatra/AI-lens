import os
import torch
import numpy as np
from typing import List, Union
import logging
from PIL import Image
import io

logger = logging.getLogger(__name__)

# Global variables for model and device
model = None
preprocess = None
device = None
clip_available = False

try:
    import clip
    clip_available = True
    logger.info("CLIP library is available")
except ImportError:
    logger.warning("CLIP library not available. Install with: pip install git+https://github.com/openai/CLIP.git")
    clip_available = False

# Global variables for model and device
model = None
preprocess = None
device = None

def load_clip_model():
    """Load CLIP model once at startup"""
    global model, preprocess, device
    
    if not clip_available:
        raise Exception("CLIP library not available. Install with: pip install git+https://github.com/openai/CLIP.git")
    
    try:
        device = "cuda" if torch.cuda.is_available() else "cpu"
        logger.info(f"Loading CLIP model on device: {device}")
        
        model, preprocess = clip.load("ViT-B/32", device=device)
        logger.info("CLIP model loaded successfully")
    except Exception as e:
        logger.error(f"Failed to load CLIP model: {e}")
        raise

# Load model at module import (only if CLIP is available)
if clip_available:
    try:
        load_clip_model()
    except Exception as e:
        logger.warning(f"Could not load CLIP model at startup: {e}")

async def get_image_embedding(file):
    """Generate CLIP embedding for uploaded image"""
    global model, preprocess, device
    
    if not clip_available:
        raise Exception("CLIP library not available. Install with: pip install git+https://github.com/openai/CLIP.git")
    
    if model is None:
        try:
            load_clip_model()
        except Exception as e:
            logger.error(f"Failed to load CLIP model: {e}")
            raise Exception("CLIP model not available")
    
    try:
        # Read and preprocess image
        contents = await file.read()
        image = Image.open(io.BytesIO(contents)).convert("RGB")
        image_input = preprocess(image).unsqueeze(0).to(device)
        
        # Generate embedding
        with torch.no_grad():
            image_features = model.encode_image(image_input)
            image_features = image_features / image_features.norm(dim=-1, keepdim=True)
        
        # Convert to numpy array
        embedding = image_features.cpu().numpy().flatten()
        
        logger.info(f"Generated image embedding with shape: {embedding.shape}")
        return embedding.tolist()
        
    except Exception as e:
        logger.error(f"Error generating image embedding: {e}")
        raise Exception(f"Failed to generate image embedding: {str(e)}")
    finally:
        # Reset file pointer
        await file.seek(0)

def get_text_embedding(text: str):
    """Generate CLIP embedding for text"""
    global model, device
    
    if not clip_available:
        raise Exception("CLIP library not available. Install with: pip install git+https://github.com/openai/CLIP.git")
    
    if model is None:
        try:
            load_clip_model()
        except Exception as e:
            logger.error(f"Failed to load CLIP model: {e}")
            raise Exception("CLIP model not available")
    
    try:
        # Tokenize and encode text
        text_input = clip.tokenize([text]).to(device)
        
        with torch.no_grad():
            text_features = model.encode_text(text_input)
            text_features = text_features / text_features.norm(dim=-1, keepdim=True)
        
        # Convert to numpy array
        embedding = text_features.cpu().numpy().flatten()
        
        logger.info(f"Generated text embedding with shape: {embedding.shape}")
        return embedding.tolist()
        
    except Exception as e:
        logger.error(f"Error generating text embedding: {e}")
        raise Exception(f"Failed to generate text embedding: {str(e)}")

def calculate_similarity(embedding1: List[float], embedding2: List[float]) -> float:
    """Calculate cosine similarity between two embeddings"""
    try:
        # Convert to numpy arrays
        emb1 = np.array(embedding1)
        emb2 = np.array(embedding2)
        
        # Calculate cosine similarity
        similarity = np.dot(emb1, emb2) / (np.linalg.norm(emb1) * np.linalg.norm(emb2))
        
        return float(similarity)
    except Exception as e:
        logger.error(f"Error calculating similarity: {e}")
        raise Exception(f"Failed to calculate similarity: {str(e)}")