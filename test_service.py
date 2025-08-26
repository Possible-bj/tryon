#!/usr/bin/env python3
"""
Test script for Styled AI Data Science Processing Service

This script tests the basic functionality of the service without requiring
actual AI models or image processing.
"""

import asyncio
import json
import base64
from pathlib import Path
import sys

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

from styled_ai.core.models import (
    ProcessingRequest, UserMeasurements, FabricProperties, 
    GarmentType, FabricMaterial
)
from styled_ai.core.processor import TryOnProcessor

def create_test_image(width: int = 100, height: int = 100) -> str:
    """Create a simple test image as base64 string"""
    # Create a simple colored rectangle as a test image
    from PIL import Image, ImageDraw
    
    # Create a simple test image
    img = Image.new('RGB', (width, height), color='white')
    draw = ImageDraw.Draw(img)
    
    # Draw a simple pattern
    draw.rectangle([10, 10, width-10, height-10], outline='black', width=2)
    draw.ellipse([20, 20, width-20, height-20], fill='blue')
    
    # Convert to base64
    import io
    buffer = io.BytesIO()
    img.save(buffer, format='JPEG')
    img_data = buffer.getvalue()
    
    return f"data:image/jpeg;base64,{base64.b64encode(img_data).decode()}"

def create_test_request() -> ProcessingRequest:
    """Create a test processing request"""
    return ProcessingRequest(
        avatar_image=create_test_image(200, 400),  # Avatar image
        garment_image=create_test_image(150, 200),  # Garment image
        user_measurements=UserMeasurements(
            height=170.0,
            weight=65.0,
            chest=95.0,
            waist=80.0,
            hips=95.0,
            shoulder_width=45.0,
            arm_length=65.0
        ),
        garment_type=GarmentType.SHIRT,
        fabric_properties=FabricProperties(
            material=FabricMaterial.COTTON,
            stretch=0.1,
            thickness="medium",
            weight=200.0,
            opacity=1.0
        )
    )

async def test_service():
    """Test the Styled AI service"""
    print("🧪 Testing Styled AI Data Science Processing Service")
    print("=" * 60)
    
    try:
        # Initialize processor
        print("1. Initializing processor...")
        processor = TryOnProcessor()
        await processor.initialize()
        print("   ✅ Processor initialized successfully")
        
        # Check model status
        print("\n2. Checking model status...")
        model_status = await processor.get_model_status()
        print(f"   📊 Models loaded: {len(model_status)}")
        for model in model_status:
            print(f"      - {model.model_name}: {model.status}")
        
        # Create test request
        print("\n3. Creating test request...")
        test_request = create_test_request()
        print(f"   📝 Request ID: {test_request.request_id}")
        print(f"   👕 Garment type: {test_request.garment_type}")
        print(f"   📏 User height: {test_request.user_measurements.height}cm")
        
        # Test fit analysis
        print("\n4. Testing fit analysis...")
        fit_analysis = await processor.analyze_fit(test_request)
        print(f"   🎯 Fit score: {fit_analysis.fit_score:.2f}")
        print(f"   ⭐ Fit quality: {fit_analysis.fit_quality}")
        print(f"   📊 Confidence: {fit_analysis.confidence:.2f}")
        
        # Test size recommendation
        print("\n5. Testing size recommendation...")
        size_rec = await processor.get_size_recommendation(test_request)
        print(f"   📏 Recommended size: {size_rec.recommended_size}")
        print(f"   🎯 Confidence: {size_rec.confidence:.2f}")
        print(f"   🔄 Alternative sizes: {', '.join(size_rec.alternative_sizes)}")
        
        # Test full try-on processing
        print("\n6. Testing full try-on processing...")
        result = await processor.process_try_on(test_request)
        print(f"   ✅ Processing completed: {result.status}")
        print(f"   ⏱️  Processing time: {result.processing_metadata.processing_time:.2f}s")
        print(f"   🎯 Quality score: {result.processing_metadata.quality_score:.2f}")
        
        # Test metrics
        print("\n7. Testing service metrics...")
        metrics = await processor.get_metrics()
        print(f"   📊 Total requests: {metrics['total_requests']}")
        print(f"   ✅ Successful: {metrics['successful_requests']}")
        print(f"   ❌ Failed: {metrics['failed_requests']}")
        print(f"   ⏱️  Avg processing time: {metrics['avg_processing_time']:.2f}s")
        
        # Cleanup
        print("\n8. Cleaning up...")
        await processor.cleanup()
        print("   ✅ Cleanup completed")
        
        print("\n🎉 All tests passed successfully!")
        print("\nThe Styled AI service is working correctly.")
        print("You can now integrate this service with your backend application.")
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

def main():
    """Main function"""
    print("Styled AI - Data Science Processing Service")
    print("Test Suite")
    print()
    
    # Run tests
    success = asyncio.run(test_service())
    
    if success:
        print("\n✅ Service test completed successfully!")
        sys.exit(0)
    else:
        print("\n❌ Service test failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()
