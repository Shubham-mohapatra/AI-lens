#  AI Lens - Visual Intelligence API

A comprehensive AI-powered visual intelligence system inspired by Apple's Visual Intelligence, built with FastAPI. This project provides advanced image analysis capabilities including captioning, object detection, text extraction, and intelligent image search.

![Python](https://img.shields.io/badge/python-v3.11+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)
![License](https://img.shields.io/badge/license-MIT-blue.svg)

##  Features

###  Visual Intelligence
- **Smart Image Analysis** - Comprehensive image understanding and categorization
- **Object Detection & Identification** - YOLO-powered object recognition
- **Text Extraction & Translation** - OCR with multi-language support
- **Landmark Recognition** - Identify famous places and locations
- **Nature Identification** - Recognize plants, animals, and natural features
- **Food Analysis** - Identify dishes with nutritional information
- **Shopping Assistant** - Product identification and search

###  AI-Powered Services
- **Image Captioning** - BLIP model for detailed image descriptions
- **Internet Image Search** - Pixabay API integration for similar image discovery
- **LLM Enhancement** - Google Gemini for contextual summaries
- **Batch Processing** - Handle multiple images simultaneously
- **Real-time Processing** - Fast analysis with caching support

###  Technical Features
- **RESTful API** - Clean, documented FastAPI endpoints
- **Docker Support** - Easy deployment with containerization
- **Rate Limiting** - Built-in request throttling
- **Error Handling** - Comprehensive error management
- **Caching System** - In-memory caching for performance
- **Health Monitoring** - System health checks

##  Quick Start

### Prerequisites
- Python 3.11+
- Virtual environment (recommended)
- API Keys for full functionality (optional for demo mode)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/Shubham-mohapatra/AI-lens.git
   cd AI-lens
   ```

2. **Set up virtual environment**
   ```bash
   python -m venv venv
   
   # Windows
   venv\Scripts\activate
   
   # macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

4. **Configure environment variables**
   Create a `.env` file in the backend directory:
   ```env
   # Optional API Keys (app works in demo mode without them)
   HUGGINGFACE_TOKEN=your_huggingface_token
   PIXABAY_API_KEY=your_pixabay_api_key
   GEMINI_API_KEY=your_gemini_api_key
   
   # Server Configuration
   DEBUG=true
   HOST=0.0.0.0
   PORT=8000
   ```

5. **Run the application**
   ```bash
   python run.py
   ```

The API will be available at:
- **API**: http://localhost:8000
- **Interactive Docs**: http://localhost:8000/docs
- **Visual Interface**: http://localhost:8000/visual_intelligence_interface.html

##  API Documentation

### Core Endpoints

#### Visual Intelligence
```http
POST /visual/analyze
```
Comprehensive image analysis with multiple AI services

#### Image Analysis
```http
POST /analyze/caption
```
Generate descriptive captions using BLIP model

#### Image Search
```http
POST /search/image
```
Find similar images using Pixabay API

#### LLM Services
```http
POST /llm/summary
```
Generate enhanced summaries using Google Gemini

#### Batch Processing
```http
POST /batch/analyze-multiple
```
Process multiple images simultaneously

### Example Usage

**Image Captioning:**
```bash
curl -X POST "http://localhost:8000/analyze/caption" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@your-image.jpg"
```

**Visual Intelligence Analysis:**
```bash
curl -X POST "http://localhost:8000/visual/analyze" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@your-image.jpg" \
  -F "analysis_type=comprehensive"
```

##  Docker Deployment

### Using Docker Compose (Recommended)
```bash
cd backend
docker-compose up -d
```

### Using Docker directly
```bash
cd backend
docker build -t ai-lens .
docker run -p 8000:8000 ai-lens
```

##  Demo Mode

The application works even without API keys! It provides:
- ✅ Image captioning with BLIP
- ✅ Object detection with YOLO
- ✅ OCR text extraction
- ✅ Demo search results
- ✅ Basic LLM responses

Simply run the application and start uploading images!

##  Project Structure

```
AI-lens/
├── backend/
│   ├── app/
│   │   ├── routers/          # API route handlers
│   │   ├── services/         # Core AI services
│   │   ├── config.py         # Configuration
│   │   ├── models.py         # Data models
│   │   └── main.py          # FastAPI application
│   ├── requirements.txt      # Python dependencies
│   ├── run.py               # Application runner
│   ├── Dockerfile           # Docker configuration
│   └── README.md            # Backend documentation
└── README.md                # Project overview
```

##  Configuration Options

### Environment Variables
- `HUGGINGFACE_TOKEN` - For BLIP model access
- `PIXABAY_API_KEY` - For image search (20k free requests/month)
- `GEMINI_API_KEY` - For LLM-powered summaries
- `DEBUG` - Enable debug mode
- `MAX_IMAGE_SIZE` - Maximum upload size (default: 10MB)
- `RATE_LIMIT_REQUESTS` - Requests per minute limit

### API Limits
- **Image Size**: 10MB maximum
- **Batch Processing**: 10 images per request
- **Rate Limiting**: 100 requests per minute per IP

##  Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

##  License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

##  Acknowledgments

- **Salesforce BLIP** - Image captioning model
- **Ultralytics YOLO** - Object detection
- **Google Gemini** - LLM services
- **Pixabay** - Free image search API
- **FastAPI** - Modern Python web framework

##  Support

If you encounter any issues or have questions:
-  Create an issue on GitHub
-  Check the [documentation](http://localhost:8000/docs) for detailed API info
-  Review the demo interface for usage examples

---

<div align="center">
  <b>Built with ❤️ by Shubham Mohapatra</b>
  <br>
  ⭐ Star this repo if you find it useful!
</div>