"""
Simple Virtual Try-On App
Building this step by step!
"""

from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
import uvicorn
import base64
import io
from PIL import Image
import uuid
from datetime import datetime

# Create simple FastAPI app
app = FastAPI(
    title="Simple Virtual Try-On",
    description="A simple app to test virtual try-on functionality",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Simple storage for demo (in real app, use database)
uploaded_images = {}

@app.get("/", response_class=HTMLResponse)
async def home():
    """Simple home page"""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Simple Virtual Try-On</title>
        <style>
            body { font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }
            .upload-section { border: 2px dashed #ccc; padding: 20px; margin: 20px 0; text-align: center; }
            .image-preview { max-width: 300px; margin: 10px; }
            button { background: #007bff; color: white; padding: 10px 20px; border: none; border-radius: 5px; cursor: pointer; }
            button:hover { background: #0056b3; }
        </style>
    </head>
    <body>
        <h1>🎨 Simple Virtual Try-On</h1>
        <p>Upload an avatar image and a garment image to test the service!</p>
        
        <div class="upload-section">
            <h3>Avatar Image</h3>
            <input type="file" id="avatarInput" accept="image/*">
            <br><br>
            <img id="avatarPreview" class="image-preview" style="display: none;">
        </div>
        
        <div class="upload-section">
            <h3>Garment Image</h3>
            <input type="file" id="garmentInput" accept="image/*">
            <br><br>
            <img id="garmentPreview" class="image-preview" style="display: none;">
        </div>
        
        <button onclick="processImages()">🚀 Process Try-On</button>
        
        <div id="result" style="margin-top: 20px;"></div>
        
        <script>
            // Preview images
            document.getElementById('avatarInput').addEventListener('change', function(e) {
                const file = e.target.files[0];
                if (file) {
                    const reader = new FileReader();
                    reader.onload = function(e) {
                        document.getElementById('avatarPreview').src = e.target.result;
                        document.getElementById('avatarPreview').style.display = 'block';
                    };
                    reader.readAsDataURL(file);
                }
            });
            
            document.getElementById('garmentInput').addEventListener('change', function(e) {
                const file = e.target.files[0];
                if (file) {
                    const reader = new FileReader();
                    reader.onload = function(e) {
                        document.getElementById('garmentPreview').src = e.target.result;
                        document.getElementById('garmentPreview').style.display = 'block';
                    };
                    reader.readAsDataURL(file);
                }
            });
            
            async function processImages() {
                const avatarFile = document.getElementById('avatarInput').files[0];
                const garmentFile = document.getElementById('garmentInput').files[0];
                
                if (!avatarFile || !garmentFile) {
                    alert('Please select both avatar and garment images!');
                    return;
                }
                
                const formData = new FormData();
                formData.append('avatar_image', avatarFile);
                formData.append('garment_image', garmentFile);
                
                try {
                    const response = await fetch('/process/try-on', {
                        method: 'POST',
                        body: formData
                    });
                    
                    const result = await response.json();
                    document.getElementById('result').innerHTML = `
                        <h3>✅ Processing Complete!</h3>
                        <p><strong>Request ID:</strong> ${result.request_id}</p>
                        <p><strong>Status:</strong> ${result.status}</p>
                        <p><strong>Message:</strong> ${result.message}</p>
                        <p><strong>Processing Time:</strong> ${result.processing_time}s</p>
                    `;
                } catch (error) {
                    document.getElementById('result').innerHTML = `
                        <h3>❌ Error</h3>
                        <p>${error.message}</p>
                    `;
                }
            }
        </script>
    </body>
    </html>
    """

@app.get("/health")
async def health_check():
    """Simple health check"""
    return {
        "status": "healthy",
        "service": "Simple Virtual Try-On",
        "timestamp": datetime.now().isoformat()
    }

@app.post("/process/try-on")
async def process_try_on(
    avatar_image: UploadFile = File(...),
    garment_image: UploadFile = File(...)
):
    """
    Simple try-on processing endpoint
    
    For now, just validates the images and returns a mock response.
    Later we'll add real AI processing!
    """
    
    # Validate file types
    if not avatar_image.content_type.startswith('image/'):
        raise HTTPException(status_code=400, detail="Avatar must be an image file")
    
    if not garment_image.content_type.startswith('image/'):
        raise HTTPException(status_code=400, detail="Garment must be an image file")
    
    # Generate unique request ID
    request_id = str(uuid.uuid4())
    
    # Store images (in real app, save to disk/database)
    uploaded_images[request_id] = {
        "avatar": avatar_image.filename,
        "garment": garment_image.filename,
        "timestamp": datetime.now()
    }
    
    # For now, just return a mock response
    # Later we'll add real AI processing here!
    return {
        "request_id": request_id,
        "status": "completed",
        "message": "Images received successfully! (AI processing coming soon...)",
        "processing_time": 0.1,
        "avatar_filename": avatar_image.filename,
        "garment_filename": garment_image.filename
    }

@app.get("/images/{request_id}")
async def get_uploaded_images(request_id: str):
    """Get info about uploaded images"""
    if request_id not in uploaded_images:
        raise HTTPException(status_code=404, detail="Request not found")
    
    return uploaded_images[request_id]

if __name__ == "__main__":
    print("🚀 Starting Simple Virtual Try-On App...")
    print("📱 Open your browser to: http://localhost:8000")
    print("🔧 API docs at: http://localhost:8000/docs")
    
    uvicorn.run(
        "simple_app:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
