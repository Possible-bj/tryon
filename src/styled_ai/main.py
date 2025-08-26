"""
Styled AI - Data Science Processing Service
Main FastAPI application for virtual try-on processing
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import logging
import os

from .core.processor import TryOnProcessor
from .core.models import ProcessingRequest, ProcessingResponse, ProcessingStatus
from .utils.config import get_settings
from .utils.logging import setup_logging

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)

# Initialize settings
settings = get_settings()

# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="AI-powered virtual try-on processing service",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize processor
try_on_processor = TryOnProcessor()

# Ensure model cache directory exists
os.makedirs(settings.MODEL_CACHE_DIR, exist_ok=True)

@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    logger.info("Starting Styled AI Data Science Service...")
    try:
        await try_on_processor.initialize()
        logger.info("Service initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize service: {e}")
        raise

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("Shutting down Styled AI Data Science Service...")
    await try_on_processor.cleanup()

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "models_loaded": try_on_processor.models_loaded
    }

@app.get("/models/status")
async def get_model_status():
    """Get AI model status and health"""
    try:
        status = await try_on_processor.get_model_status()
        return status
    except Exception as e:
        logger.error(f"Error getting model status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/process/try-on", response_model=ProcessingResponse)
async def process_try_on(
    request: ProcessingRequest
):
    """
    Process virtual try-on request
    
    Receives avatar and garment images, processes them using AI models,
    and returns the try-on result with fit analysis.
    """
    try:
        logger.info(f"Processing try-on request: {request.request_id}")
        
        # Process the request
        result = await try_on_processor.process_try_on(request)
        
        return result
        
    except Exception as e:
        logger.error(f"Error processing try-on request: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/process/fit-analysis")
async def analyze_fit(request: ProcessingRequest):
    """
    Analyze garment fit on avatar
    
    Provides detailed fit analysis without generating the full try-on image.
    """
    try:
        logger.info(f"Analyzing fit for request: {request.request_id}")
        
        result = await try_on_processor.analyze_fit(request)
        
        return result
        
    except Exception as e:
        logger.error(f"Error analyzing fit: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/process/size-recommendation")
async def get_size_recommendation(request: ProcessingRequest):
    """
    Get size recommendations based on fit analysis
    
    Analyzes the fit and provides size suggestions for the garment.
    """
    try:
        logger.info(f"Getting size recommendation for request: {request.request_id}")
        
        result = await try_on_processor.get_size_recommendation(request)
        
        return result
        
    except Exception as e:
        logger.error(f"Error getting size recommendation: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/process/batch")
async def process_batch(requests: list[ProcessingRequest]):
    """
    Process multiple try-on requests in batch
    
    Useful for processing multiple garments for the same avatar.
    """
    try:
        logger.info(f"Processing batch of {len(requests)} requests")
        
        results = await try_on_processor.process_batch(requests)
        
        return {
            "batch_id": f"batch_{len(requests)}_{hash(str(requests))}",
            "total_requests": len(requests),
            "results": results
        }
        
    except Exception as e:
        logger.error(f"Error processing batch: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/process/status/{job_id}")
async def get_processing_status(job_id: str):
    """Get the status of a processing job"""
    try:
        status = await try_on_processor.get_job_status(job_id)
        return status
    except Exception as e:
        logger.error(f"Error getting job status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/process/history")
async def get_processing_history(limit: int = 100, offset: int = 0):
    """Get processing history and analytics"""
    try:
        history = await try_on_processor.get_processing_history(limit, offset)
        return history
    except Exception as e:
        logger.error(f"Error getting processing history: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/metrics")
async def get_metrics():
    """Get service metrics and performance data"""
    try:
        metrics = await try_on_processor.get_metrics()
        return metrics
    except Exception as e:
        logger.error(f"Error getting metrics: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower()
    )
