"""
Core data models for Styled AI processing service
"""

from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any, Union
from datetime import datetime
from enum import Enum
import uuid
import re

class ProcessingStatus(str, Enum):
    """Processing job status"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class FitQuality(str, Enum):
    """Fit quality assessment"""
    POOR = "poor"
    FAIR = "fair"
    GOOD = "good"
    EXCELLENT = "excellent"

class GarmentType(str, Enum):
    """Types of garments"""
    SHIRT = "shirt"
    PANTS = "pants"
    DRESS = "dress"
    JACKET = "jacket"
    SKIRT = "skirt"
    SHORTS = "shorts"
    SWEATER = "sweater"
    COAT = "coat"
    BLOUSE = "blouse"
    JEANS = "jeans"

class FabricMaterial(str, Enum):
    """Fabric material types"""
    COTTON = "cotton"
    SILK = "silk"
    WOOL = "wool"
    POLYESTER = "polyester"
    LINEN = "linen"
    DENIM = "denim"
    VELVET = "velvet"
    LEATHER = "leather"
    SUEDE = "suede"
    SYNTHETIC = "synthetic"

class UserMeasurements(BaseModel):
    """User body measurements for fit analysis"""
    height: float = Field(..., ge=100, le=250, description="Height in cm")
    weight: float = Field(..., ge=30, le=200, description="Weight in kg")
    chest: float = Field(..., ge=60, le=150, description="Chest circumference in cm")
    waist: float = Field(..., ge=50, le=150, description="Waist circumference in cm")
    hips: float = Field(..., ge=60, le=150, description="Hip circumference in cm")
    shoulder_width: Optional[float] = Field(None, ge=30, le=80, description="Shoulder width in cm")
    arm_length: Optional[float] = Field(None, ge=40, le=100, description="Arm length in cm")
    inseam: Optional[float] = Field(None, ge=50, le=100, description="Inseam length in cm")
    neck: Optional[float] = Field(None, ge=25, le=50, description="Neck circumference in cm")

    @validator('height', 'weight', 'chest', 'waist', 'hips')
    def validate_positive(cls, v):
        if v <= 0:
            raise ValueError('Value must be positive')
        return v

class ImageInput(BaseModel):
    """Flexible image input - accepts base64 or URL"""
    image_data: str = Field(..., description="Image as base64 string or URL")
    
    @validator('image_data')
    def validate_image_input(cls, v):
        """Validate that input is either base64 or valid URL"""
        # Check if it's base64 (starts with data:image/ or just base64 string)
        if v.startswith('data:image/') or len(v) > 100:  # Base64 images are typically long
            return v
        
        # Check if it's a valid URL
        url_pattern = re.compile(
            r'^https?://'  # http:// or https://
            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
            r'localhost|'  # localhost...
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
            r'(?::\d+)?'  # optional port
            r'(?:/?|[/?]\S+)$', re.IGNORECASE)
        
        if url_pattern.match(v):
            return v
        
        raise ValueError('Image input must be either base64 encoded image or valid URL')

class FabricProperties(BaseModel):
    """Fabric properties for simulation"""
    material: FabricMaterial
    stretch: float = Field(0.0, ge=0.0, le=1.0, description="Stretch factor (0-1)")
    thickness: str = Field("medium", description="Fabric thickness: thin, medium, thick")
    weight: Optional[float] = Field(None, ge=0, description="Fabric weight in g/m²")
    texture: Optional[str] = Field(None, description="Fabric texture description")
    opacity: float = Field(1.0, ge=0.0, le=1.0, description="Opacity factor (0-1)")

class ProcessingRequest(BaseModel):
    """Request for virtual try-on processing"""
    request_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    avatar_image: Union[str, ImageInput] = Field(..., description="Avatar image as base64 string, URL, or ImageInput object")
    garment_image: Union[str, ImageInput] = Field(..., description="Garment image as base64 string, URL, or ImageInput object")
    user_measurements: UserMeasurements
    garment_type: GarmentType
    fabric_properties: FabricProperties
    processing_options: Optional[Dict[str, Any]] = Field(default_factory=dict)
    user_preferences: Optional[Dict[str, Any]] = Field(default_factory=dict)
    
    class Config:
        schema_extra = {
            "example": {
                "avatar_image": "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQ...",
                "garment_image": "https://example.com/garment.png",
                "user_measurements": {
                    "height": 170.0,
                    "weight": 65.0,
                    "chest": 95.0,
                    "waist": 80.0,
                    "hips": 95.0
                },
                "garment_type": "shirt",
                "fabric_properties": {
                    "material": "cotton",
                    "stretch": 0.1,
                    "thickness": "medium"
                }
            }
        }

class FitAnalysis(BaseModel):
    """Detailed fit analysis results"""
    fit_score: float = Field(..., ge=0.0, le=1.0, description="Overall fit score (0-1)")
    fit_quality: FitQuality
    areas_of_concern: List[str] = Field(default_factory=list, description="Areas with fit issues")
    recommendations: List[str] = Field(default_factory=list, description="Fit improvement suggestions")
    detailed_metrics: Dict[str, float] = Field(default_factory=dict, description="Detailed fit metrics by body area")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence in fit analysis")

class SizeRecommendation(BaseModel):
    """Size recommendation results"""
    recommended_size: str = Field(..., description="Recommended garment size")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence in recommendation")
    alternative_sizes: List[str] = Field(default_factory=list, description="Alternative size options")
    fit_notes: str = Field(..., description="Detailed fit notes")
    size_chart: Optional[Dict[str, Any]] = Field(None, description="Size chart reference")

class ProcessingMetadata(BaseModel):
    """Metadata about the processing job"""
    model_version: str = Field(..., description="Version of AI model used")
    processing_time: float = Field(..., description="Processing time in seconds")
    quality_score: float = Field(..., ge=0.0, le=1.0, description="Output quality score")
    processing_steps: List[str] = Field(default_factory=list, description="Processing steps completed")
    model_confidence: float = Field(..., ge=0.0, le=1.0, description="Model confidence in result")

class ProcessingResponse(BaseModel):
    """Response from virtual try-on processing"""
    request_id: str
    status: ProcessingStatus
    try_on_result: Optional[str] = Field(None, description="Base64 encoded processed image")
    fit_analysis: FitAnalysis
    size_recommendation: SizeRecommendation
    processing_metadata: ProcessingMetadata
    error_message: Optional[str] = Field(None, description="Error message if processing failed")
    created_at: datetime = Field(default_factory=datetime.utcnow)

class ModelStatus(BaseModel):
    """AI model status information"""
    model_name: str
    version: str
    status: str = Field(..., description="Model status: loaded, loading, error")
    loaded_at: Optional[datetime] = None
    performance_metrics: Dict[str, Any] = Field(default_factory=dict)
    memory_usage: Optional[float] = None
    gpu_available: bool = False
    last_updated: Optional[datetime] = None

class ProcessingJob(BaseModel):
    """Processing job information"""
    job_id: str
    request_id: str
    status: ProcessingStatus
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    progress: float = Field(0.0, ge=0.0, le=1.0)
    error_message: Optional[str] = None

class BatchProcessingRequest(BaseModel):
    """Batch processing request"""
    batch_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    requests: List[ProcessingRequest]
    priority: int = Field(1, ge=1, le=10, description="Processing priority (1-10)")
    callback_url: Optional[str] = Field(None, description="Callback URL for completion notification")

class BatchProcessingResponse(BaseModel):
    """Batch processing response"""
    batch_id: str
    total_requests: int
    completed_requests: int
    failed_requests: int
    results: List[ProcessingResponse]
    batch_status: ProcessingStatus
    created_at: datetime
    completed_at: Optional[datetime] = None
