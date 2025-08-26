"""
Core processor for virtual try-on AI processing
"""

import asyncio
import logging
import time
from datetime import datetime
from typing import List, Optional, Dict, Any, Union
import base64
import io
from PIL import Image
import numpy as np

from .models import (
    ProcessingRequest, ProcessingResponse, ProcessingStatus,
    FitAnalysis, SizeRecommendation, ProcessingMetadata,
    FitQuality, ModelStatus, ProcessingJob, ImageInput
)
from ..utils.config import get_settings
from ..processors.simple_image_processor import SimpleImageProcessor
from ..processors.simple_fit_analyzer import SimpleFitAnalyzer
from ..processors.simple_size_recommender import SimpleSizeRecommender
from ..models.simple_model_manager import SimpleModelManager

logger = logging.getLogger(__name__)

class TryOnProcessor:
    """
    Main processor for virtual try-on AI processing
    
    Coordinates image processing, fit analysis, and size recommendations
    using various AI models and computer vision techniques.
    """
    
    def __init__(self):
        self.settings = get_settings()
        self.models_loaded = False
        
        # Initialize components
        self.image_processor = SimpleImageProcessor()
        self.fit_analyzer = SimpleFitAnalyzer()
        self.size_recommender = SimpleSizeRecommender()
        self.model_manager = SimpleModelManager()
        
        # Job tracking
        self.active_jobs: Dict[str, ProcessingJob] = {}
        self.processing_history: List[ProcessingJob] = []
        
        # In-memory image storage
        self.image_cache: Dict[str, Dict[str, Any]] = {}
        self.max_cache_size = self.settings.MAX_CACHE_SIZE
        self.cache_cleanup_threshold = self.settings.CACHE_CLEANUP_THRESHOLD
        
        # Performance metrics
        self.total_requests = 0
        self.successful_requests = 0
        self.failed_requests = 0
        self.avg_processing_time = 0.0
        
    async def initialize(self):
        """Initialize the processor and load AI models"""
        try:
            logger.info("Initializing TryOnProcessor...")
            
            # Initialize model manager
            await self.model_manager.initialize()
            
            # Initialize processors
            await self.image_processor.initialize()
            await self.fit_analyzer.initialize()
            await self.size_recommender.initialize()
            
            self.models_loaded = True
            logger.info("TryOnProcessor initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize TryOnProcessor: {e}")
            raise
    
    async def cleanup(self):
        """Cleanup resources"""
        try:
            logger.info("Cleaning up TryOnProcessor...")
            
            # Cleanup components
            await self.image_processor.cleanup()
            await self.fit_analyzer.cleanup()
            await self.size_recommender.cleanup()
            await self.model_manager.cleanup()
            
            # Clear image cache
            await self._clear_image_cache()
            
            logger.info("TryOnProcessor cleanup completed")
            
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")
    
    async def _clear_image_cache(self):
        """Clear all cached images from memory"""
        try:
            cache_size = len(self.image_cache)
            self.image_cache.clear()
            logger.info(f"Cleared {cache_size} cached images from memory")
        except Exception as e:
            logger.error(f"Error clearing image cache: {e}")
    
    async def _cleanup_old_cache_entries(self):
        """Remove old cache entries when cache gets too large"""
        try:
            if len(self.image_cache) > self.cache_cleanup_threshold:
                # Remove oldest entries (keep only the most recent ones)
                sorted_entries = sorted(
                    self.image_cache.items(), 
                    key=lambda x: x[1].get('timestamp', 0)
                )
                
                # Keep only the most recent entries
                entries_to_remove = len(self.image_cache) - self.max_cache_size
                entries_to_remove = min(entries_to_remove, len(sorted_entries))
                for i in range(entries_to_remove):
                    del self.image_cache[sorted_entries[i][0]]
                
                logger.info(f"Cleaned up {entries_to_remove} old cache entries")
        except Exception as e:
            logger.error(f"Error cleaning up old cache entries: {e}")
    
    async def _cache_images(self, request_id: str, avatar_img: np.ndarray, garment_img: np.ndarray):
        """Cache processed images in memory"""
        try:
            # Cleanup old entries if cache is getting full
            await self._cleanup_old_cache_entries()
            
            # Cache the images with metadata
            self.image_cache[request_id] = {
                'avatar': avatar_img,
                'garment': garment_img,
                'timestamp': time.time(),
                'size_mb': (avatar_img.nbytes + garment_img.nbytes) / (1024 * 1024)  # Size in MB
            }
            
            logger.info(f"Cached images for request {request_id}, cache size: {len(self.image_cache)}")
        except Exception as e:
            logger.error(f"Error caching images for request {request_id}: {e}")
    
    async def _cleanup_request_images(self, request_id: str):
        """Cleanup cached images for a specific request"""
        try:
            if request_id in self.image_cache:
                cached_data = self.image_cache[request_id]
                size_mb = cached_data.get('size_mb', 0)
                del self.image_cache[request_id]
                logger.info(f"Cleaned up cached images for request {request_id} (freed {size_mb:.2f} MB)")
        except Exception as e:
            logger.error(f"Error cleaning up cached images for request {request_id}: {e}")
    
    async def process_try_on(self, request: ProcessingRequest) -> ProcessingResponse:
        """
        Process a complete virtual try-on request
        
        Args:
            request: Processing request with avatar and garment images
            
        Returns:
            ProcessingResponse with try-on result and analysis
        """
        start_time = time.time()
        job_id = f"job_{request.request_id}"
        
        try:
            # Create job tracking
            job = ProcessingJob(
                job_id=job_id,
                request_id=request.request_id,
                status=ProcessingStatus.PROCESSING,
                created_at=datetime.utcnow(),
                started_at=datetime.utcnow()
            )
            self.active_jobs[job_id] = job
            
            logger.info(f"Processing try-on request: {request.request_id}")
            
            # Step 1: Preprocess images and cache them
            avatar_img = await self._preprocess_avatar(request.avatar_image)
            garment_img = await self._preprocess_garment(request.garment_image)
            
            # Cache the processed images
            await self._cache_images(request.request_id, avatar_img, garment_img)
            
            # Step 2: Generate try-on result
            try_on_result = await self._generate_try_on(
                avatar_img, garment_img, request
            )
            
            # Step 3: Analyze fit
            fit_analysis = await self._analyze_fit(
                avatar_img, garment_img, request.user_measurements, request
            )
            
            # Step 4: Get size recommendations
            size_recommendation = await self._get_size_recommendation(
                fit_analysis, request
            )
            
            # Calculate processing time
            processing_time = time.time() - start_time
            
            # Create response
            response = ProcessingResponse(
                request_id=request.request_id,
                status=ProcessingStatus.COMPLETED,
                try_on_result=try_on_result,
                fit_analysis=fit_analysis,
                size_recommendation=size_recommendation,
                processing_metadata=ProcessingMetadata(
                    model_version="v1.0.0",
                    processing_time=processing_time,
                    quality_score=fit_analysis.confidence,
                    processing_steps=["preprocessing", "try_on_generation", "fit_analysis", "size_recommendation"],
                    model_confidence=fit_analysis.confidence
                )
            )
            
            # Update job status
            job.status = ProcessingStatus.COMPLETED
            job.completed_at = datetime.utcnow()
            job.progress = 1.0
            
            # Update metrics
            self._update_metrics(processing_time, True)
            
            # Cleanup cached images after successful processing
            await self._cleanup_request_images(request_id=job_id)
            
            logger.info(f"Successfully processed try-on request: {request.request_id}")
            return response
            
        except Exception as e:
            processing_time = time.time() - start_time
            error_msg = str(e)
            
            logger.error(f"Error processing try-on request {request.request_id}: {error_msg}")
            
            # Update job status
            job.status = ProcessingStatus.FAILED
            job.completed_at = datetime.utcnow()
            job.error_message = error_msg
            
            # Update metrics
            self._update_metrics(processing_time, False)
            
            # Return error response
            return ProcessingResponse(
                request_id=request.request_id,
                status=ProcessingStatus.FAILED,
                fit_analysis=FitAnalysis(
                    fit_score=0.0,
                    fit_quality=FitQuality.POOR,
                    confidence=0.0
                ),
                size_recommendation=SizeRecommendation(
                    recommended_size="unknown",
                    confidence=0.0,
                    fit_notes="Processing failed"
                ),
                processing_metadata=ProcessingMetadata(
                    model_version="v1.0.0",
                    processing_time=processing_time,
                    quality_score=0.0,
                    processing_steps=[],
                    model_confidence=0.0
                ),
                error_message=error_msg
            )
        
        finally:
            # Move job to history
            if job_id in self.active_jobs:
                self.processing_history.append(self.active_jobs.pop(job_id))
            
            # Always cleanup cached images, even on error
            await self._cleanup_request_images(request.request_id)
    
    async def analyze_fit(self, request: ProcessingRequest) -> FitAnalysis:
        """Analyze garment fit without generating full try-on image"""
        try:
            logger.info(f"Analyzing fit for request: {request.request_id}")
            
            # Preprocess images
            avatar_img = await self._preprocess_avatar(request.avatar_image)
            garment_img = await self._preprocess_garment(request.garment_image)
            
            # Analyze fit
            fit_analysis = await self._analyze_fit(
                avatar_img, garment_img, request.user_measurements, request
            )
            
            return fit_analysis
            
        except Exception as e:
            logger.error(f"Error analyzing fit: {e}")
            raise
    
    async def get_size_recommendation(self, request: ProcessingRequest) -> SizeRecommendation:
        """Get size recommendations based on fit analysis"""
        try:
            logger.info(f"Getting size recommendation for request: {request.request_id}")
            
            # First analyze fit
            fit_analysis = await self.analyze_fit(request)
            
            # Get size recommendation
            size_recommendation = await self._get_size_recommendation(
                fit_analysis, request
            )
            
            return size_recommendation
            
        except Exception as e:
            logger.error(f"Error getting size recommendation: {e}")
            raise
    
    async def process_batch(self, requests: List[ProcessingRequest]) -> List[ProcessingResponse]:
        """Process multiple requests in batch"""
        try:
            logger.info(f"Processing batch of {len(requests)} requests")
            
            # Process requests concurrently
            tasks = [self.process_try_on(req) for req in requests]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Handle any exceptions
            processed_results = []
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    logger.error(f"Batch request {i} failed: {result}")
                    # Create error response
                    error_response = ProcessingResponse(
                        request_id=requests[i].request_id,
                        status=ProcessingStatus.FAILED,
                        fit_analysis=FitAnalysis(
                            fit_score=0.0,
                            fit_quality=FitQuality.POOR,
                            confidence=0.0
                        ),
                        size_recommendation=SizeRecommendation(
                            recommended_size="unknown",
                            confidence=0.0,
                            fit_notes="Processing failed"
                        ),
                        processing_metadata=ProcessingMetadata(
                            model_version="v1.0.0",
                            processing_time=0.0,
                            quality_score=0.0,
                            processing_steps=[],
                            model_confidence=0.0
                        ),
                        error_message=str(result)
                    )
                    processed_results.append(error_response)
                else:
                    processed_results.append(result)
            
            return processed_results
            
        except Exception as e:
            logger.error(f"Error processing batch: {e}")
            raise
    
    async def get_job_status(self, job_id: str) -> Optional[ProcessingJob]:
        """Get the status of a processing job"""
        # Check active jobs
        if job_id in self.active_jobs:
            return self.active_jobs[job_id]
        
        # Check history
        for job in self.processing_history:
            if job.job_id == job_id:
                return job
        
        return None
    
    async def get_processing_history(self, limit: int = 100, offset: int = 0) -> Dict[str, Any]:
        """Get processing history and analytics"""
        total_jobs = len(self.processing_history)
        jobs = self.processing_history[offset:offset + limit]
        
        # Calculate statistics
        completed_jobs = sum(1 for job in jobs if job.status == ProcessingStatus.COMPLETED)
        failed_jobs = sum(1 for job in jobs if job.status == ProcessingStatus.FAILED)
        
        return {
            "total_jobs": total_jobs,
            "returned_jobs": len(jobs),
            "offset": offset,
            "limit": limit,
            "completed_jobs": completed_jobs,
            "failed_jobs": failed_jobs,
            "jobs": jobs
        }
    
    async def get_metrics(self) -> Dict[str, Any]:
        """Get service metrics and performance data"""
        return {
            "total_requests": self.total_requests,
            "successful_requests": self.successful_requests,
            "failed_requests": self.failed_requests,
            "success_rate": self.successful_requests / max(self.total_requests, 1),
            "avg_processing_time": self.avg_processing_time,
            "active_jobs": len(self.active_jobs),
            "models_loaded": self.models_loaded,
            "model_status": await self.model_manager.get_status(),
            "memory_cache": {
                "cached_images": len(self.image_cache),
                "max_cache_size": self.max_cache_size,
                "cache_cleanup_threshold": self.cache_cleanup_threshold,
                "total_cache_size_mb": sum(entry.get('size_mb', 0) for entry in self.image_cache.values())
            }
        }
    
    async def get_model_status(self) -> List[ModelStatus]:
        """Get AI model status and health"""
        return await self.model_manager.get_status()
    
    # Private helper methods
    
    async def _extract_image_data(self, image_input: Union[str, ImageInput]) -> str:
        """Extract image data from either base64 string or URL"""
        if isinstance(image_input, ImageInput):
            return image_input.image_data
        return image_input
    
    async def _download_image_from_url(self, url: str) -> bytes:
        """Download image from URL and return as bytes"""
        import aiohttp
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    if response.status == 200:
                        return await response.read()
                    else:
                        raise ValueError(f"Failed to download image from {url}: HTTP {response.status}")
        except Exception as e:
            logger.error(f"Error downloading image from {url}: {e}")
            raise ValueError(f"Failed to download image from {url}: {str(e)}")
    
    async def _preprocess_avatar(self, avatar_image: Union[str, ImageInput]) -> np.ndarray:
        """Preprocess avatar image for processing"""
        try:
            # Extract image data (base64 or URL)
            image_data_str = await self._extract_image_data(avatar_image)
            
            # Check if it's a URL or base64
            if image_data_str.startswith(('http://', 'https://')):
                # Download image from URL
                image_bytes = await self._download_image_from_url(image_data_str)
                image = Image.open(io.BytesIO(image_bytes))
            else:
                # Decode base64 image
                image_data = base64.b64decode(image_data_str.split(',')[1] if ',' in image_data_str else image_data_str)
                image = Image.open(io.BytesIO(image_data))
            
            # Convert to RGB if needed
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Resize to standard dimensions
            image = image.resize((self.settings.AVATAR_WIDTH, self.settings.AVATAR_HEIGHT))
            
            # Convert to numpy array
            avatar_array = np.array(image)
            
            return avatar_array
            
        except Exception as e:
            logger.error(f"Error preprocessing avatar: {e}")
            raise
    
    async def _preprocess_garment(self, garment_image: Union[str, ImageInput]) -> np.ndarray:
        """Preprocess garment image for processing"""
        try:
            # Extract image data (base64 or URL)
            image_data_str = await self._extract_image_data(garment_image)
            
            # Check if it's a URL or base64
            if image_data_str.startswith(('http://', 'https://')):
                # Download image from URL
                image_bytes = await self._download_image_from_url(image_data_str)
                image = Image.open(io.BytesIO(image_bytes))
            else:
                # Decode base64 image
                image_data = base64.b64decode(image_data_str.split(',')[1] if ',' in image_data_str else image_data_str)
                image = Image.open(io.BytesIO(image_data))
            
            # Convert to RGB if needed
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Resize to standard dimensions
            image = image.resize((self.settings.GARMENT_RESOLUTION, self.settings.GARMENT_RESOLUTION))
            
            # Convert to numpy array
            garment_array = np.array(image)
            
            return garment_array
            
        except Exception as e:
            logger.error(f"Error preprocessing garment: {e}")
            raise
    
    async def _generate_try_on(
        self, 
        avatar_img: np.ndarray, 
        garment_img: np.ndarray, 
        request: ProcessingRequest
    ) -> str:
        """Generate virtual try-on result"""
        try:
            # Use image processor to generate try-on
            result_image = await self.image_processor.generate_try_on(
                avatar_img, garment_img, request
            )
            
            # Convert result to base64
            result_pil = Image.fromarray(result_image)
            buffer = io.BytesIO()
            result_pil.save(buffer, format='JPEG', quality=self.settings.AVATAR_QUALITY)
            result_base64 = base64.b64encode(buffer.getvalue()).decode()
            
            return f"data:image/jpeg;base64,{result_base64}"
            
        except Exception as e:
            logger.error(f"Error generating try-on: {e}")
            raise
    
    async def _analyze_fit(
        self, 
        avatar_img: np.ndarray, 
        garment_img: np.ndarray, 
        measurements: Any, 
        request: ProcessingRequest
    ) -> FitAnalysis:
        """Analyze garment fit on avatar"""
        try:
            # Use fit analyzer to analyze fit
            fit_analysis = await self.fit_analyzer.analyze_fit(
                avatar_img, garment_img, measurements, request
            )
            
            return fit_analysis
            
        except Exception as e:
            logger.error(f"Error analyzing fit: {e}")
            raise
    
    async def _get_size_recommendation(
        self, 
        fit_analysis: FitAnalysis, 
        request: ProcessingRequest
    ) -> SizeRecommendation:
        """Get size recommendations based on fit analysis"""
        try:
            # Use size recommender to get recommendations
            size_recommendation = await self.size_recommender.get_recommendation(
                fit_analysis, request
            )
            
            return size_recommendation
            
        except Exception as e:
            logger.error(f"Error getting size recommendation: {e}")
            raise
    
    def _update_metrics(self, processing_time: float, success: bool):
        """Update performance metrics"""
        self.total_requests += 1
        if success:
            self.successful_requests += 1
        else:
            self.failed_requests += 1
        
        # Update average processing time
        if self.successful_requests > 0:
            self.avg_processing_time = (
                (self.avg_processing_time * (self.successful_requests - 1) + processing_time) 
                / self.successful_requests
            )
