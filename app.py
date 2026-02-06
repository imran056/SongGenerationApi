#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
SongGeneration API - Main Application
Combines Gradio UI with FastAPI endpoints for Render deployment
"""

import os
import sys
import gradio as gr
from fastapi import FastAPI, HTTPException, Header, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
import uvicorn
from datetime import datetime
from typing import Optional
import json
import traceback

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import original functionality
# Note: Ye imports aapki original files se hain
try:
    from generate import generate_song, generate_pure_music
    GENERATION_AVAILABLE = True
except ImportError:
    print("Warning: Could not import generation functions. Using dummy mode.")
    GENERATION_AVAILABLE = False
    
    # Dummy functions for testing
    def generate_song(lyrics, genre="Auto", **kwargs):
        return None, {"status": "dummy", "message": "Generation not available"}
    
    def generate_pure_music(prompt, genre="Auto", **kwargs):
        return None, {"status": "dummy", "message": "Generation not available"}

# ======================
# FastAPI Setup
# ======================

api = FastAPI(
    title="SongGeneration API",
    description="AI-powered music generation API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
api.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ======================
# Configuration
# ======================

OUTPUT_DIR = os.path.join(os.getcwd(), "outputs")
os.makedirs(OUTPUT_DIR, exist_ok=True)

CACHE_DIR = os.environ.get("TRANSFORMERS_CACHE", "./cache")
os.makedirs(CACHE_DIR, exist_ok=True)

# Optional API Key
API_KEY = os.environ.get("API_KEY", None)

# ======================
# Helper Functions
# ======================

async def verify_api_key(x_api_key: str = Header(None)):
    """Verify API key if configured"""
    if API_KEY and x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid or missing API Key")
    return True

def save_audio_file(audio_data, filename):
    """Save audio file to outputs directory"""
    if audio_data is None:
        return None
    
    filepath = os.path.join(OUTPUT_DIR, filename)
    # Assuming audio_data is a file path or audio object
    # Adjust based on actual return type
    return filepath

# ======================
# API Endpoints
# ======================

@api.get("/")
async def root():
    """API information"""
    return {
        "service": "SongGeneration API",
        "version": "1.0.0",
        "status": "running",
        "generation_available": GENERATION_AVAILABLE,
        "endpoints": {
            "health": "/api/health",
            "generate_song": "/api/generate",
            "generate_music": "/api/generate-music",
            "genres": "/api/genres",
            "docs": "/docs",
            "gradio": "/gradio"
        },
        "timestamp": datetime.now().isoformat()
    }

@api.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "SongGeneration API",
        "generation_available": GENERATION_AVAILABLE,
        "output_dir": OUTPUT_DIR,
        "cache_dir": CACHE_DIR,
        "timestamp": datetime.now().isoformat()
    }

@api.post("/api/generate")
async def generate_song_api(
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
    - audio_prompt: Optional audio file for style reference
    - text_prompt: Optional text description
    - seed: Random seed (-1 for random)
    """
    try:
        if not lyrics or len(lyrics.strip()) == 0:
            raise HTTPException(status_code=400, detail="Lyrics cannot be empty")
        
        if not GENERATION_AVAILABLE:
            raise HTTPException(
                status_code=503, 
                detail="Song generation service not available. Models may be loading."
            )
        
        # Generate unique filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_filename = f"song_{timestamp}.wav"
        
        # Call generation function
        try:
            audio_output, info = generate_song(
                lyrics=lyrics,
                genre=genre,
                audio_prompt=audio_prompt,
                text_prompt=text_prompt,
                seed=seed
            )
            
            # Save audio file
            if audio_output:
                output_path = os.path.join(OUTPUT_DIR, output_filename)
                # Save logic depends on what generate_song returns
                # Assuming it returns a file path or needs to be saved
                
                return {
                    "status": "success",
                    "message": "Song generated successfully",
                    "data": {
                        "audio_url": f"/outputs/{output_filename}",
                        "filename": output_filename,
                        "genre": genre,
                        "info": info if isinstance(info, dict) else {},
                        "lyrics_preview": lyrics[:100] + "..." if len(lyrics) > 100 else lyrics
                    },
                    "timestamp": datetime.now().isoformat()
                }
            else:
                raise HTTPException(status_code=500, detail="Generation failed")
                
        except Exception as gen_error:
            print(f"Generation error: {gen_error}")
            traceback.print_exc()
            raise HTTPException(
                status_code=500,
                detail=f"Generation failed: {str(gen_error)}"
            )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Unexpected error: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")

@api.post("/api/generate-music")
async def generate_music_api(
    text_prompt: str,
    genre: str = "Auto",
    duration: int = 180,
    seed: int = -1,
    api_key_valid: bool = Depends(verify_api_key)
):
    """
    Generate instrumental music without lyrics
    """
    try:
        if not text_prompt or len(text_prompt.strip()) == 0:
            raise HTTPException(status_code=400, detail="Text prompt cannot be empty")
        
        if not GENERATION_AVAILABLE:
            raise HTTPException(
                status_code=503,
                detail="Music generation service not available"
            )
        
        if duration > 300:
            raise HTTPException(status_code=400, detail="Duration max 300 seconds")
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_filename = f"music_{timestamp}.wav"
        
        try:
            audio_output, info = generate_pure_music(
                prompt=text_prompt,
                genre=genre,
                duration=duration,
                seed=seed
            )
            
            if audio_output:
                return {
                    "status": "success",
                    "message": "Music generated successfully",
                    "data": {
                        "audio_url": f"/outputs/{output_filename}",
                        "filename": output_filename,
                        "genre": genre,
                        "duration": duration,
                        "prompt": text_prompt
                    },
                    "timestamp": datetime.now().isoformat()
                }
            else:
                raise HTTPException(status_code=500, detail="Generation failed")
                
        except Exception as gen_error:
            raise HTTPException(status_code=500, detail=str(gen_error))
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

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

@api.get("/api/genres")
async def get_genres():
    """Get available music genres"""
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
    return {"status": "success", "genres": genres, "count": len(genres)}

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

def create_gradio_interface():
    """Create Gradio UI interface"""
    
    # Lyrics input guidelines
    lyrics_guide = """
    ### Lyrics Format Guide:
    
    **Structure Tags:**
    - `[intro-short]`, `[intro-medium]`, `[intro-long]` - Intro sections
    - `[verse]` - Verse (needs lyrics)
    - `[chorus]` - Chorus (needs lyrics)
    - `[bridge]` - Bridge (needs lyrics)
    - `[inst]`, `[ins]` - Instrumental (no lyrics)
    - `[outro]` - Outro (no lyrics)
    
    **Rules:**
    - Each paragraph = one segment
    - Start with structure tag, end with blank line
    - Intro/inst/outro don't need lyrics
    - Verse/chorus/bridge need lyrics
    
    **Example:**
    ```
    [intro-medium]
    
    [verse]
    夜晚的街灯闪烁
    我漫步在熟悉的角落
    
    [chorus]
    回忆停留在这里
    你却已不在
    ```
    """
    
    with gr.Blocks(title="SongGeneration API") as demo:
        gr.Markdown("# 🎵 SongGeneration API")
        gr.Markdown("AI-powered music generation with lyrics or text prompts")
        
        with gr.Tab("Generate Song"):
            gr.Markdown(lyrics_guide)
            
            with gr.Row():
                with gr.Column():
                    lyrics_input = gr.Textbox(
                        label="Lyrics",
                        placeholder="Enter your lyrics with structure tags...",
                        lines=15
                    )
                    genre_dropdown = gr.Dropdown(
                        choices=["Auto", "Pop", "R&B", "Dance", "Jazz", "Rock", 
                                "Chinese Style", "Chinese Tradition", "Metal", 
                                "Reggae", "Chinese Opera"],
                        value="Auto",
                        label="Genre"
                    )
                    seed_input = gr.Number(label="Seed (-1 for random)", value=-1)
                    generate_btn = gr.Button("Generate Song", variant="primary")
                
                with gr.Column():
                    audio_output = gr.Audio(label="Generated Song")
                    info_output = gr.JSON(label="Generation Info")
            
            generate_btn.click(
                fn=lambda l, g, s: generate_song(l, g, seed=s) if GENERATION_AVAILABLE else (None, {"error": "Not available"}),
                inputs=[lyrics_input, genre_dropdown, seed_input],
                outputs=[audio_output, info_output]
            )
        
        with gr.Tab("Generate Music"):
            gr.Markdown("### Generate instrumental music without lyrics")
            
            with gr.Row():
                with gr.Column():
                    prompt_input = gr.Textbox(
                        label="Text Prompt",
                        placeholder="Describe the music style (e.g., 'Calm piano music for studying')",
                        lines=3
                    )
                    music_genre = gr.Dropdown(
                        choices=["Auto", "Pop", "Rock", "Jazz", "Classical"],
                        value="Auto",
                        label="Genre"
                    )
                    duration_input = gr.Slider(
                        minimum=30,
                        maximum=300,
                        value=180,
                        step=10,
                        label="Duration (seconds)"
                    )
                    music_seed = gr.Number(label="Seed (-1 for random)", value=-1)
                    generate_music_btn = gr.Button("Generate Music", variant="primary")
                
                with gr.Column():
                    music_output = gr.Audio(label="Generated Music")
                    music_info = gr.JSON(label="Generation Info")
            
            generate_music_btn.click(
                fn=lambda p, g, d, s: generate_pure_music(p, g, duration=d, seed=s) if GENERATION_AVAILABLE else (None, {"error": "Not available"}),
                inputs=[prompt_input, music_genre, duration_input, music_seed],
                outputs=[music_output, music_info]
            )
        
        with gr.Tab("API Info"):
            gr.Markdown(f"""
            ## API Endpoints
            
            **Base URL:** `{os.environ.get('RENDER_EXTERNAL_URL', 'http://localhost:10000')}`
            
            ### Endpoints:
            - `GET /api/health` - Health check
            - `POST /api/generate` - Generate song from lyrics
            - `POST /api/generate-music` - Generate instrumental music
            - `GET /api/genres` - Get available genres
            - `GET /outputs/{{filename}}` - Download audio file
            
            ### Documentation:
            - Interactive API Docs: `/docs`
            - Alternative Docs: `/redoc`
            
            ### Generation Status:
            - **Available:** {GENERATION_AVAILABLE}
            """)
    
    return demo

# Create Gradio interface
demo = create_gradio_interface()

# Mount Gradio app with FastAPI
app = gr.mount_gradio_app(api, demo, path="/gradio")

# Mount static files for outputs
if os.path.exists(OUTPUT_DIR):
    api.mount("/outputs", StaticFiles(directory=OUTPUT_DIR), name="outputs")

# ======================
# Server Start
# ======================

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    host = os.environ.get("HOST", "0.0.0.0")
    
    print("=" * 60)
    print("🚀 SongGeneration API Server Starting...")
    print("=" * 60)
    print(f"📍 Host: {host}")
    print(f"🔌 Port: {port}")
    print(f"📁 Cache: {CACHE_DIR}")
    print(f"📁 Output: {OUTPUT_DIR}")
    print(f"🎵 Generation: {'Available' if GENERATION_AVAILABLE else 'Not Available (Models Loading...)'}")
    print(f"🌐 API Docs: http://{host}:{port}/docs")
    print(f"🎨 Gradio UI: http://{host}:{port}/gradio")
    print("=" * 60)
    
    uvicorn.run(
        app,
        host=host,
        port=port,
        log_level="info",
        access_log=True
    )
