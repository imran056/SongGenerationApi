"""
SongGeneration API Client - Python Example
Ye file dikhaati hai ke kaise API ko use karein
"""

import requests
import json
import os
from typing import Optional

class SongGenerationClient:
    """Client for SongGeneration API"""
    
    def __init__(self, base_url: str, api_key: Optional[str] = None):
        """
        Initialize client
        
        Args:
            base_url: API server ka URL (e.g., https://your-app.onrender.com)
            api_key: Optional API key for authentication
        """
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self.headers = {
            "Content-Type": "application/json"
        }
        
        if api_key:
            self.headers["X-API-Key"] = api_key
    
    def health_check(self):
        """Check if API is healthy"""
        try:
            response = requests.get(f"{self.base_url}/api/health")
            return response.json()
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def generate_song(
        self,
        lyrics: str,
        genre: str = "Auto",
        audio_prompt: Optional[str] = None,
        text_prompt: Optional[str] = None,
        seed: int = -1
    ):
        """
        Generate a song from lyrics
        
        Args:
            lyrics: Song lyrics with structure tags
            genre: Music genre
            audio_prompt: Optional audio file for style reference
            text_prompt: Optional text description
            seed: Random seed (-1 for random)
            
        Returns:
            dict: API response with song information
        """
        endpoint = f"{self.base_url}/api/generate"
        
        payload = {
            "lyrics": lyrics,
            "genre": genre,
            "seed": seed
        }
        
        if audio_prompt:
            payload["audio_prompt"] = audio_prompt
        
        if text_prompt:
            payload["text_prompt"] = text_prompt
        
        try:
            response = requests.post(
                endpoint,
                json=payload,
                headers=self.headers,
                timeout=300  # 5 minutes timeout
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                return {
                    "status": "error",
                    "message": response.text,
                    "status_code": response.status_code
                }
        except Exception as e:
            return {
                "status": "error",
                "message": str(e)
            }
    
    def generate_pure_music(
        self,
        text_prompt: str,
        genre: str = "Auto",
        duration: int = 180,
        seed: int = -1
    ):
        """
        Generate instrumental music without lyrics
        
        Args:
            text_prompt: Description of music style/mood
            genre: Music genre
            duration: Duration in seconds
            seed: Random seed
            
        Returns:
            dict: API response with music information
        """
        endpoint = f"{self.base_url}/api/generate-pure-music"
        
        payload = {
            "text_prompt": text_prompt,
            "genre": genre,
            "duration": duration,
            "seed": seed
        }
        
        try:
            response = requests.post(
                endpoint,
                json=payload,
                headers=self.headers,
                timeout=300
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                return {
                    "status": "error",
                    "message": response.text,
                    "status_code": response.status_code
                }
        except Exception as e:
            return {
                "status": "error",
                "message": str(e)
            }
    
    def download_audio(self, audio_url: str, output_path: str):
        """
        Download generated audio file
        
        Args:
            audio_url: URL returned from generate_song
            output_path: Local path to save file
        """
        try:
            # If relative URL, make it absolute
            if audio_url.startswith('/'):
                audio_url = f"{self.base_url}{audio_url}"
            
            response = requests.get(audio_url, stream=True)
            
            if response.status_code == 200:
                with open(output_path, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)
                return {"status": "success", "path": output_path}
            else:
                return {
                    "status": "error",
                    "message": "Failed to download audio"
                }
        except Exception as e:
            return {
                "status": "error",
                "message": str(e)
            }
    
    def get_genres(self):
        """Get list of available genres"""
        try:
            response = requests.get(f"{self.base_url}/api/genres")
            return response.json()
        except Exception as e:
            return {"status": "error", "message": str(e)}


# ======================
# Usage Examples
# ======================

def example_generate_song():
    """Example: Generate a Chinese style song"""
    
    # Initialize client
    client = SongGenerationClient(
        base_url="https://your-app.onrender.com",
        api_key=None  # Set if you've configured API key
    )
    
    # Check health
    health = client.health_check()
    print("Health Check:", health)
    
    # Chinese lyrics
    lyrics = """[intro-medium]

[verse]
夜晚的街灯闪烁
我漫步在熟悉的角落
回忆像潮水般涌来
你的笑容如此温柔
在心头无法抹去

[chorus]
回忆停留在这里
你却已不在
我的心被爱填满
却又被思念念念缠绕
"""
    
    # Generate song
    print("\nGenerating song...")
    result = client.generate_song(
        lyrics=lyrics,
        genre="Chinese Style",
        seed=42  # For reproducibility
    )
    
    print("\nResult:", json.dumps(result, indent=2, ensure_ascii=False))
    
    # Download audio if successful
    if result.get("status") == "success":
        audio_url = result["data"]["audio_url"]
        output_path = "generated_song.wav"
        
        print(f"\nDownloading audio to {output_path}...")
        download_result = client.download_audio(audio_url, output_path)
        print("Download:", download_result)


def example_generate_music():
    """Example: Generate instrumental music"""
    
    client = SongGenerationClient(
        base_url="https://your-app.onrender.com"
    )
    
    # Generate pure music
    result = client.generate_pure_music(
        text_prompt="Calm and peaceful piano music for studying",
        genre="Pop",
        duration=120
    )
    
    print("Music Generation:", json.dumps(result, indent=2))


def example_batch_generation():
    """Example: Generate multiple songs"""
    
    client = SongGenerationClient(
        base_url="https://your-app.onrender.com"
    )
    
    # List of lyrics
    lyrics_list = [
        {
            "lyrics": "[verse]\nFirst song lyrics here\n[chorus]\nChorus here",
            "genre": "Pop",
            "name": "song_1"
        },
        {
            "lyrics": "[verse]\nSecond song lyrics here\n[chorus]\nChorus here",
            "genre": "Rock",
            "name": "song_2"
        }
    ]
    
    for i, item in enumerate(lyrics_list):
        print(f"\nGenerating song {i+1}/{len(lyrics_list)}...")
        
        result = client.generate_song(
            lyrics=item["lyrics"],
            genre=item["genre"]
        )
        
        if result.get("status") == "success":
            audio_url = result["data"]["audio_url"]
            output_path = f"{item['name']}.wav"
            
            client.download_audio(audio_url, output_path)
            print(f"✓ {item['name']} generated and saved")
        else:
            print(f"✗ {item['name']} failed:", result.get("message"))


def example_with_error_handling():
    """Example with comprehensive error handling"""
    
    client = SongGenerationClient(
        base_url="https://your-app.onrender.com"
    )
    
    lyrics = """[intro-medium]
[verse]
Sample lyrics here
"""
    
    try:
        # Health check first
        health = client.health_check()
        if health.get("status") != "healthy":
            print("API is not healthy!")
            return
        
        # Generate song
        result = client.generate_song(
            lyrics=lyrics,
            genre="Auto"
        )
        
        if result.get("status") == "success":
            print("✓ Song generated successfully!")
            print(f"Audio URL: {result['data']['audio_url']}")
            
            # Download
            audio_url = result["data"]["audio_url"]
            download_result = client.download_audio(
                audio_url,
                "output.wav"
            )
            
            if download_result.get("status") == "success":
                print(f"✓ Audio saved to: {download_result['path']}")
            else:
                print(f"✗ Download failed: {download_result['message']}")
        else:
            print(f"✗ Generation failed: {result.get('message')}")
            
    except Exception as e:
        print(f"✗ Error: {str(e)}")


if __name__ == "__main__":
    print("SongGeneration API Client Examples\n" + "="*50)
    
    # Run examples (uncomment to use)
    # example_generate_song()
    # example_generate_music()
    # example_batch_generation()
    # example_with_error_handling()
    
    print("\nTo use this client:")
    print("1. Replace 'https://your-app.onrender.com' with your actual Render URL")
    print("2. Uncomment and run the example you want to try")
    print("3. Make sure the API is deployed and running")
