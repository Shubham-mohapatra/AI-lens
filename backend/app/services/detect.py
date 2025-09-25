import torch
import cv2
import numpy as np
from PIL import Image
import io
import logging
from typing import List, Dict
from ultralytics import YOLO

logger = logging.getLogger(__name__)

# Global YOLO model
model = None

def load_detection_model():
    """Load YOLO model once at startup"""
    global model
    try:
        logger.info("Loading YOLO model...")
        model = YOLO('yolov8n.pt')  # Use nano model for faster inference
        logger.info("YOLO model loaded successfully")
    except Exception as e:
        logger.error(f"Failed to load YOLO model: {e}")
        raise

# Load model at module import
try:
    load_detection_model()
except Exception as e:
    logger.warning(f"Could not load detection model at startup: {e}")

async def detect_objects(file, confidence_threshold: float = 0.5) -> List[Dict]:
    """Detect objects in uploaded image using YOLO"""
    global model
    
    if model is None:
        try:
            load_detection_model()
        except Exception as e:
            logger.error(f"Failed to load detection model: {e}")
            raise Exception("Object detection model not available")
    
    try:
        # Read image data
        contents = await file.read()
        image = Image.open(io.BytesIO(contents)).convert("RGB")
        
        # Convert PIL to numpy array
        image_array = np.array(image)
        
        # Perform detection
        results = model(image_array, conf=confidence_threshold)
        
        # Format results
        detections = []
        for result in results:
            boxes = result.boxes
            if boxes is not None:
                for box in boxes:
                    # Get bounding box coordinates
                    x1, y1, x2, y2 = box.xyxy[0].tolist()
                    
                    # Get class name and confidence
                    class_id = int(box.cls[0])
                    class_name = model.names[class_id]
                    confidence = float(box.conf[0])
                    
                    detections.append({
                        "class": class_name,
                        "confidence": confidence,
                        "bbox": {
                            "x1": x1,
                            "y1": y1,
                            "x2": x2,
                            "y2": y2
                        }
                    })
        
        logger.info(f"Detected {len(detections)} objects")
        return detections
        
    except Exception as e:
        logger.error(f"Error detecting objects: {e}")
        raise Exception(f"Failed to detect objects: {str(e)}")
    finally:
        # Reset file pointer
        await file.seek(0)

def get_object_counts(detections: List[Dict]) -> Dict[str, int]:
    """Count objects by class"""
    counts = {}
    for detection in detections:
        class_name = detection["class"]
        counts[class_name] = counts.get(class_name, 0) + 1
    return counts

def filter_detections_by_confidence(detections: List[Dict], min_confidence: float) -> List[Dict]:
    """Filter detections by minimum confidence threshold"""
    return [d for d in detections if d["confidence"] >= min_confidence]