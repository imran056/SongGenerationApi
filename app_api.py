"""
SongGeneration API - Modified for Render Deployment
Original: https://huggingface.co/spaces/tencent/SongGeneration
Modified with FastAPI endpoints for external API access
"""

import os
import gradio as gr
from fastapi import FastAPI, HTTPException, Header, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
import uvicorn
from datetime import datetime
from typing import Optional
import json

# Import original app functionality
# Note: Ye imports original app.py se hain
# Aapko original code se ye functions import karne honge
# from original_app import generate, AudioPrompt, TextPrompt, etc.

# ======================
# FastAPI Setup
# ======================

api = FastAPI(
    title="SongGeneration API",
    description="API for generating songs using AI",
    version="1.0.0"
)

# CORS middleware - external access ke liye
api.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Production mein specific domains allow karein
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ======================
# Configuration
# ======================

# Output directory for generated songs
OUTPUT_DIR = os.path.join(os.getcwd(), "outputs")
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Cache configuration
CACHE_DIR = os.environ.get("TRANSFORMERS_CACHE", "./cache")
os.makedirs(CACHE_DIR, exist_ok=True)

# ======================
# Helper Functions
# ======================

def save_generated_audio(audio_data, filename="generated_song.wav"):
    """Save generated audio to file"""
    filepath = os.path.join(OUTPUT_DIR, filename)
    # Audio save karne ka logic
    # Ye original app ke code pe depend karega
    return filepath

def validate_lyrics(lyrics: str) -> bool:
    """Validate lyrics format"""
    if not lyrics or len(lyrics.strip()) == 0:
        return False
    return True

# ======================
# API Key Authentication (Optional)
# ======================

API_KEY = os.environ.get("API_KEY", None)

async def verify_api_key(x_api_key: str = Header(None)):
    """Verify API key if configured"""
    if API_KEY and x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid or missing API Key")
    return True

# ======================
# API Endpoints
# ======================

@api.get("/")
async def root():
    """Root endpoint - API information"""
    return {
        "service": "SongGeneration API",
        "version": "1.0.0",
        "status": "running",
        "endpoints": {
            "generate_song": "/api/generate",
            "health": "/api/health",
            "docs": "/docs",
            "gradio_ui": "/gradio"
        },
        "timestamp": datetime.now().isoformat()
    }

@api.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "SongGeneration",
        "timestamp": datetime.now().isoformat(),
        "cache_dir": CACHE_DIR,
        "output_dir": OUTPUT_DIR
    }

@api.post("/api/generate")
async def generate_song(
    lyrics: str,
    genre: str = "Auto",
    audio_prompt: Optional[str] = None,
    text_prompt: Optional[str] = None,
    seed: int = -1,
    api_key_valid: bool = Depends(verify_api_key)
):
    """
    Generate a song from lyrics
    
    Parameters:
    - lyrics: Song lyrics with structure tags ([intro], [verse], [chorus], etc.)
    - genre: Music genre (Auto, Pop, Rock, Chinese Style, etc.)
    - audio_prompt: Optional audio file URL/path for style reference
    - text_prompt: Optional text description for music style
    - seed: Random seed for reproducibility (-1 for random)
    
    Returns:
    - JSON with generated song information and download URL
    """
    try:
        # Validate input
        if not validate_lyrics(lyrics):
            raise HTTPException(
                status_code=400, 
                detail="Invalid lyrics. Please provide proper lyrics with structure tags."
            )
        
        # Generate unique filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_filename = f"song_{timestamp}.wav"
        
        # Call the original generate function
        # Note: Ye function aapko original app.py se import karna hoga
        # result = generate(
        #     lyrics=lyrics,
        #     genre=genre,
        #     audio_prompt=audio_prompt,
        #     text_prompt=text_prompt,
        #     seed=seed
        # )
        
        # Dummy response for template
        # Replace this with actual generation logic
        result = {
            "audio_path": os.path.join(OUTPUT_DIR, output_filename),
            "info": {
                "genre": genre,
                "duration": "3:30",
                "lyrics_length": len(lyrics),
                "seed": seed if seed != -1 else "random"
            }
        }
        
        # Generate song URL
        song_url = f"/outputs/{output_filename}"
        
        return {
            "status": "success",
            "message": "Song generated successfully",
            "data": {
                "audio_url": song_url,
                "filename": output_filename,
                "genre": genre,
                "info": result.get("info", {}),
                "lyrics": lyrics[:100] + "..." if len(lyrics) > 100 else lyrics
            },
            "timestamp": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Song generation failed: {str(e)}"
        )

@api.get("/outputs/{filename}")
async def download_audio(filename: str):
    """Download generated audio file"""
    filepath = os.path.join(OUTPUT_DIR, filename)
    
    if not os.path.exists(filepath):
        raise HTTPException(status_code=404, detail="Audio file not found")
    
    return FileResponse(
        filepath,
        media_type="audio/wav",
        filename=filename
    )

@api.post("/api/generate-pure-music")
async def generate_pure_music(
    text_prompt: str,
    genre: str = "Auto",
    duration: int = 180,
    seed: int = -1,
    api_key_valid: bool = Depends(verify_api_key)
):
    """
    Generate instrumental music without lyrics
    
    Parameters:
    - text_prompt: Description of the music style/mood
    - genre: Music genre
    - duration: Duration in seconds (max 300)
    - seed: Random seed for reproducibility
    """
    try:
        if not text_prompt or len(text_prompt.strip()) == 0:
            raise HTTPException(
                status_code=400,
                detail="Text prompt is required"
            )
        
        if duration > 300:
            raise HTTPException(
                status_code=400,
                detail="Duration cannot exceed 300 seconds"
            )
        
        # Generate filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_filename = f"music_{timestamp}.wav"
        
        # Call pure music generation function
        # result = generate_pure_music_function(...)
        
        return {
            "status": "success",
            "message": "Music generated successfully",
            "data": {
                "audio_url": f"/outputs/{output_filename}",
                "filename": output_filename,
                "genre": genre,
                "duration": duration,
                "text_prompt": text_prompt
            },
            "timestamp": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Music generation failed: {str(e)}"
        )

@api.get("/api/genres")
async def get_available_genres():
    """Get list of available music genres"""
    genres = [
        "Auto",
        "Pop",
        "R&B",
        "Dance",
        "Jazz",
        "Rock",
        "Chinese Style",
        "Chinese Tradition",
        "Metal",
        "Reggae",
        "Chinese Opera"
    ]
    return {
        "status": "success",
        "genres": genres,
        "count": len(genres)
    }

@api.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Custom HTTP exception handler"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "status": "error",
            "message": exc.detail,
            "timestamp": datetime.now().isoformat()
        }
    )

# ======================
# Gradio Interface
# ======================

# Original Gradio interface
# Ye aapko original app.py se copy karna hoga
demo = gr.Interface(
    fn=lambda x: x,  # Placeholder
    inputs="text",
    outputs="text",
    title="SongGeneration Demo"
)

# Mount Gradio app
app = gr.mount_gradio_app(api, demo, path="/gradio")

# Mount static files for audio outputs
if os.path.exists(OUTPUT_DIR):
    api.mount("/outputs", StaticFiles(directory=OUTPUT_DIR), name="outputs")

# ======================
# Server Configuration
# ======================

if __name__ == "__main__":
    # Get port from environment (Render sets this)
    port = int(os.environ.get("PORT", 7860))
    host = os.environ.get("HOST", "0.0.0.0")
    
    print(f"🚀 Starting SongGeneration API Server...")
    print(f"📍 Host: {host}")
    print(f"🔌 Port: {port}")
    print(f"📁 Cache Directory: {CACHE_DIR}")
    print(f"📁 Output Directory: {OUTPUT_DIR}")
    print(f"🌐 API Docs: http://{host}:{port}/docs")
    print(f"🎨 Gradio UI: http://{host}:{port}/gradio")
    
    uvicorn.run(
        app,
        host=host,
        port=port,
        log_level="info"
    )
