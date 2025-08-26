# Styled AI - Data Science Processing Service

"Style that fits. Virtually."

## Overview

Styled AI is a **data science processing service** that provides AI-powered virtual try-on capabilities. This service receives avatar and garment images, processes them using computer vision and machine learning models, and returns fit predictions and size recommendations.

## Core Functionality

### 1. Image Processing Pipeline
- **Input**: Avatar images and garment images
- **Processing**: AI-powered garment fitting and draping simulation
- **Output**: Processed try-on images with fit analysis

### 2. Fit Prediction & Size Recommendation
- **AI Analysis**: Analyzes garment fit on avatar using computer vision
- **Size Recommendations**: Suggests best fit based on AI analysis and historical data
- **Fit Metrics**: Provides confidence scores and fit quality indicators

### 3. Data Science Models
- **Computer Vision**: Image recognition and garment segmentation
- **GANs**: Realistic try-on rendering and image synthesis
- **ML Models**: Fit prediction algorithms and size recommendation systems

## Technology Stack

### Core Processing
- **Python FastAPI**: High-performance API for processing requests
- **Computer Vision**: OpenCV, PIL for image processing
- **AI/ML**: TensorFlow/PyTorch for garment fitting models
- **Image Processing**: Advanced algorithms for realistic try-on generation

### Data Science Tools
- **NumPy/SciPy**: Numerical computing and scientific algorithms
- **Scikit-learn**: Machine learning utilities
- **OpenCV**: Computer vision and image processing
- **PIL/Pillow**: Image manipulation and processing

## API Endpoints

### Core Processing
- `POST /process/try-on`: Process avatar + garment → try-on result
- `POST /process/fit-analysis`: Analyze fit and provide recommendations
- `POST /process/size-recommendation`: Get size suggestions based on fit data

### Model Management
- `GET /models/status`: Check AI model availability and health
- `POST /models/update`: Update processing models
- `GET /models/metrics`: Get model performance metrics

### Data Processing
- `POST /process/batch`: Process multiple try-on requests
- `GET /process/status/{job_id}`: Check processing job status
- `GET /process/history`: Get processing history and analytics

## Input/Output Format

### Input
```json
{
  "avatar_image": "base64_encoded_image",
  "garment_image": "base64_encoded_image",
  "user_measurements": {
    "height": 170,
    "weight": 65,
    "chest": 95,
    "waist": 80,
    "hips": 95
  },
  "garment_type": "shirt",
  "fabric_properties": {
    "material": "cotton",
    "stretch": 0.1,
    "thickness": "medium"
  }
}
```

### Output
```json
{
  "try_on_result": "base64_encoded_processed_image",
  "fit_analysis": {
    "fit_score": 0.85,
    "fit_quality": "excellent",
    "areas_of_concern": [],
    "recommendations": ["Size fits well", "Consider length adjustment"]
  },
  "size_recommendation": {
    "recommended_size": "M",
    "confidence": 0.92,
    "alternative_sizes": ["S", "L"],
    "fit_notes": "Medium provides optimal fit for your measurements"
  },
  "processing_metadata": {
    "model_version": "v2.1.0",
    "processing_time": 2.45,
    "quality_score": 0.89
  }
}
```

## Installation

1. Create a `.env` file:
```env
SECRET_KEY=your_secret_key
TENSORFLOW_MODEL_PATH=/path/to/models
TORCH_MODEL_PATH=/path/to/models
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the processing service:
```bash
uvicorn src.styled_ai.main:app --reload
```

## Project Structure

```
ds_tjc/
├── src/
│   └── styled_ai/           # Main processing service
│       ├── core/            # Core AI processing logic
│       ├── models/          # AI/ML model management
│       ├── processors/      # Image processing pipelines
│       ├── analytics/       # Fit analysis and recommendations
│       └── utils/           # Processing utilities
├── config/                  # Configuration settings
├── models/                  # Pre-trained AI models
└── data/                    # Training and validation data
```

## Usage

This service is designed to be **integrated with a backend application** that:
- Sends avatar and garment images for processing
- Receives processed results and recommendations
- Manages user data and processing workflows
- Provides the user interface for the virtual try-on experience

## Contributing

This is a data science processing service template for building AI-powered virtual try-on capabilities. The service focuses on the core AI/ML processing logic that can be integrated with larger applications.
