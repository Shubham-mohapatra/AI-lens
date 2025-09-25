# AI Lens Backend

A comprehensive AI-powered image analysis API built with FastAPI that provides image captioning, internet image search using Pixabay API, and LLM-based summary generation.

## Features

- **Image Captioning**: Generate descriptive captions using BLIP model
- **Internet Image Search**: Search for similar images using FREE Pixabay API (20,000 requests/month)
- **LLM Services**: Enhanced summaries from image captions
- **Real-time Processing**: Fast image analysis and search capabilities
- **Demo Mode**: Works even without API key (shows placeholder results)

## API Endpoints

### Image Analysis
- `POST /api/analyze/caption` - Generate image captions
- `GET /api/analyze/health` - Health check

### Image Search  
- `POST /api/search/image` - Search for similar images on the internet using uploaded image
- `GET /api/search/health` - Health check

### LLM Services
- `POST /api/llm/summary` - Generate enhanced summaries from captions
- `GET /api/llm/health` - Health check

### General
- `GET /` - API information
- `GET /health` - Overall health check
- `GET /docs` - Interactive API documentation

## Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd ai-lens/backend
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   
   # Windows
   venv\Scripts\activate
   
   # Linux/Mac  
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   Create a `.env` file:
   ```
   HUGGINGFACE_TOKEN=your_huggingface_token_here
   # Optional: Get free API key from https://pixabay.com/api/docs/
   PIXABAY_API_KEY=your_pixabay_api_key_here
   ```

   **Getting a FREE Pixabay API Key** (Optional but recommended):
   1. Visit [Pixabay API Documentation](https://pixabay.com/api/docs/)
   2. Create a free Pixabay account
   3. Your API key will be shown on the API docs page
   4. Copy it to your `.env` file
   
   **Note**: The app works without the API key (shows demo results), but with the key you get:
   - 20,000 FREE requests per month
   - High-quality stock photos
   - No rate limits for normal usage

5. **Download models** (optional - models download automatically on first use)
   ```bash
   python -c "
   from transformers import BlipProcessor, BlipForConditionalGeneration
   BlipProcessor.from_pretrained('Salesforce/blip-image-captioning-base')
   BlipForConditionalGeneration.from_pretrained('Salesforce/blip-image-captioning-base')
   "
   ```

## Running the Server

### Development
```bash
python run.py
```

### Production
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

The API will be available at:
- **API**: http://localhost:8000
- **Documentation**: http://localhost:8000/docs
- **Alternative docs**: http://localhost:8000/redoc

## Usage Examples

### Image Captioning
```bash
curl -X POST "http://localhost:8000/api/analyze/caption" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@image.jpg"
```

### Internet Image Search (Upload Image)
```bash
curl -X POST "http://localhost:8000/api/search/image" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@image.jpg" \
  -G -d "count=10"
```

### Generate Summary from Caption
```bash
curl -X POST "http://localhost:8000/api/llm/summary" \
  -H "Content-Type: application/json" \
  -d '{"caption": "a person sitting on a bench in a park", "style": "descriptive", "max_length": 150}'
```

## How It Works

1. **Image Upload**: User uploads an image to `/api/search/image`
2. **Caption Generation**: The BLIP model generates a descriptive caption
3. **Pixabay Search**: The caption is used as a query to search Pixabay for similar images
4. **Results**: Returns a list of high-quality stock photos and images

**Demo Mode**: If no Pixabay API key is provided, the system returns placeholder demo images so you can test the functionality immediately.

## Project Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI application
│   ├── models.py            # Pydantic models
│   ├── routers/
│   │   ├── analyze.py       # Image analysis endpoints
│   │   ├── search.py        # Internet search endpoints
│   │   └── llm.py          # LLM service endpoints
│   └── services/
│       ├── caption.py       # Image captioning (BLIP)
│       ├── pixabay_search.py # Pixabay Image Search API
│       └── llm_service.py   # LLM processing
├── .env                     # Environment variables
├── requirements.txt         # Dependencies
├── run.py                  # Server startup script
└── README.md               # This file
```

## Models Used

- **BLIP**: Image captioning (Salesforce/blip-image-captioning-base)
- **Pixabay API**: Internet image search (FREE - 20,000 requests/month)

## Configuration

### Environment Variables
- `HUGGINGFACE_TOKEN`: HuggingFace API token for model access
- `PIXABAY_API_KEY`: (Optional) Pixabay API key for internet search

### CORS Settings
Currently configured to allow all origins (`*`). Update in `app/main.py` for production:
```python
allow_origins=["http://localhost:3000", "https://your-domain.com"]
```

## Development

### Adding New Services
1. Create service file in `app/services/`
2. Create router in `app/routers/`
3. Add router to `app/main.py`
4. Update models in `app/models.py`

### Testing
```bash
# Install test dependencies
pip install pytest httpx

# Run tests
pytest
```

## Troubleshooting

### Common Issues

1. **Pixabay API Issues**
   - The app works without API key (demo mode)
   - For real images: Get free API key from [pixabay.com/api/docs](https://pixabay.com/api/docs/)
   - 20,000 FREE requests per month
   - No credit card required

2. **Model Download Failures**
   - Ensure internet connection
   - Check HuggingFace token validity
   - Try manual model download

3. **CUDA/GPU Issues**
   - Models will fallback to CPU automatically
   - For GPU support, install PyTorch with CUDA

4. **File Size Limits**
   - Default limit: 10MB
   - Adjust in router files if needed

5. **Memory Issues**
   - Consider using smaller models
   - Add model unloading for memory optimization

### API Rate Limits

- **Pixabay API**: 20,000 requests/month (FREE)
- **HuggingFace**: Models are loaded locally, no API limits
- **Demo Mode**: Unlimited (uses placeholder images)

## License

[Add your license information here]

## Contributing

[Add contribution guidelines here]