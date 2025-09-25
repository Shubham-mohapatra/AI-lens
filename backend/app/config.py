import os
from typing import List
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Settings:
    """Application settings loaded from environment variables"""
    
    def __init__(self):
        # API Configuration
        self.app_name: str = "AI Lens API"
        self.app_version: str = "1.0.0"
        self.debug: bool = os.getenv("DEBUG", "false").lower() == "true"
        
        # Server Configuration
        self.host: str = os.getenv("HOST", "0.0.0.0")
        self.port: int = int(os.getenv("PORT", "8000"))
        
        # CORS Configuration
        self.allowed_origins: List[str] = os.getenv("ALLOWED_ORIGINS", "*").split(",")
        self.allowed_methods: List[str] = ["GET", "POST", "PUT", "DELETE"]
        self.allowed_headers: List[str] = ["*"]
        
        # API Keys
        self.huggingface_token: str = os.getenv("HUGGINGFACE_TOKEN", "")
        self.pixabay_api_key: str = os.getenv("PIXABAY_API_KEY", "")
        
        # Model Configuration
        self.blip_model_name: str = os.getenv("BLIP_MODEL_NAME", "Salesforce/blip-image-captioning-base")
        self.max_image_size: int = int(os.getenv("MAX_IMAGE_SIZE", str(10 * 1024 * 1024)))  # 10MB
        
        # Search Configuration
        self.default_search_count: int = int(os.getenv("DEFAULT_SEARCH_COUNT", "10"))
        self.max_search_count: int = int(os.getenv("MAX_SEARCH_COUNT", "50"))
        
        # Rate Limiting
        self.rate_limit_requests: int = int(os.getenv("RATE_LIMIT_REQUESTS", "100"))
        self.rate_limit_window: int = int(os.getenv("RATE_LIMIT_WINDOW", "60"))  # seconds
        
        # Logging
        self.log_level: str = os.getenv("LOG_LEVEL", "INFO")

# Global settings instance
settings = Settings()