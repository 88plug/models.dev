#!/usr/bin/env python3
"""
OpenAI API Sync for models.dev
Fetches latest models from OpenAI API
"""

import asyncio
import aiohttp
import tomli
import tomli_w
from pathlib import Path
from typing import Dict, List, Optional
import os


class OpenAISync:
    """Sync handler for OpenAI models"""
    
    def __init__(self, providers_dir: str = "providers"):
        self.providers_dir = Path(providers_dir)
        self.provider_name = "openai"
        self.models_dir = self.providers_dir / self.provider_name / "models"
        self.models_dir.mkdir(parents=True, exist_ok=True)
        self.api_key = os.getenv('OPENAI_API_KEY')
    
    async def fetch_models(self) -> List[Dict]:
        """Fetch available models from OpenAI API"""
        # OpenAI requires API key, so we'll use known models as fallback
        # This list can be updated as OpenAI releases new models
        
        known_models = [
            {
                "id": "gpt-4o",
                "name": "GPT-4o",
                "description": "OpenAI's most advanced multimodal model",
                "context_length": 128000,
                "capabilities": ["reasoning", "coding", "vision", "audio"],
                "pricing": {
                    "input": 2.50,   # $2.50 per million tokens
                    "output": 10.00   # $10.00 per million tokens
                }
            },
            {
                "id": "gpt-4o-mini",
                "name": "GPT-4o Mini",
                "description": "Smaller, faster version of GPT-4o",
                "context_length": 128000,
                "capabilities": ["reasoning", "coding", "vision"],
                "pricing": {
                    "input": 0.15,   # $0.15 per million tokens
                    "output": 0.60    # $0.60 per million tokens
                }
            },
            {
                "id": "gpt-4-turbo",
                "name": "GPT-4 Turbo",
                "description": "Previous generation high-performance model",
                "context_length": 128000,
                "capabilities": ["reasoning", "coding", "vision"],
                "pricing": {
                    "input": 10.00,  # $10.00 per million tokens
                    "output": 30.00   # $30.00 per million tokens
                }
            },
            {
                "id": "gpt-4",
                "name": "GPT-4",
                "description": "Original GPT-4 model",
                "context_length": 8192,
                "capabilities": ["reasoning", "coding"],
                "pricing": {
                    "input": 30.00,  # $30.00 per million tokens
                    "output": 60.00   # $60.00 per million tokens
                }
            },
            {
                "id": "gpt-3.5-turbo",
                "name": "GPT-3.5 Turbo",
                "description": "Fast and cost-effective model",
                "context_length": 16385,
                "capabilities": ["reasoning", "coding"],
                "pricing": {
                    "input": 0.50,   # $0.50 per million tokens
                    "output": 1.50    # $1.50 per million tokens
                }
            },
            {
                "id": "gpt-3.5-turbo-instruct",
                "name": "GPT-3.5 Turbo Instruct",
                "description": "Instruction-following version of GPT-3.5",
                "context_length": 4096,
                "capabilities": ["reasoning", "coding"],
                "pricing": {
                    "input": 1.50,   # $1.50 per million tokens
                    "output": 2.00    # $2.00 per million tokens
                }
            },
            {
                "id": "dall-e-3",
                "name": "DALL-E 3",
                "description": "Image generation model",
                "context_length": 4000,
                "capabilities": ["image_generation"],
                "pricing": {
                    "input": 0.04,   # $0.04 per image (standard)
                    "output": 0.08    # $0.08 per image (HD)
                }
            },
            {
                "id": "tts-1",
                "name": "TTS-1",
                "description": "Text-to-speech model",
                "context_length": 4096,
                "capabilities": ["text_to_speech"],
                "pricing": {
                    "input": 0.015,  # $0.015 per 1K characters
                    "output": 0.0     # No output cost
                }
            },
            {
                "id": "whisper-1",
                "name": "Whisper-1",
                "description": "Speech recognition model",
                "context_length": 0,  # Not applicable
                "capabilities": ["speech_recognition"],
                "pricing": {
                    "input": 0.006,  # $0.006 per minute
                    "output": 0.0     # No output cost
                }
            }
        ]
        
        # Try to fetch from API if key is available
        if self.api_key:
            try:
                async with aiohttp.ClientSession() as session:
                    headers = {
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json"
                    }
                    
                    async with session.get(
                        "https://api.openai.com/v1/models",
                        headers=headers
                    ) as response:
                        if response.status == 200:
                            data = await response.json()
                            # Process API response and merge with known models
                            api_models = []
                            for model in data.get("data", []):
                                model_id = model["id"]
                                # Map API models to our known models structure
                                known_model = next((m for m in known_models if m["id"] == model_id), None)
                                if known_model:
                                    api_models.append(known_model)
                            
                            if api_models:
                                return api_models
            except Exception as e:
                print(f"⚠️ OpenAI API fetch failed, using known models: {e}")
        
        return known_models
    
    def load_existing_model(self, model_id: str) -> Optional[Dict]:
        """Load existing model configuration if it exists"""
        model_file = self.models_dir / f"{model_id}.toml"
        
        if model_file.exists():
            with open(model_file, 'r') as f:
                return tomli.loads(f.read())
        return None
    
    def create_model_config(self, model_data: Dict, existing_config: Optional[Dict] = None) -> Dict:
        """Create or update model configuration"""
        
        # Start with existing config or create new one
        config = existing_config or {}
        
        # Update basic model information
        config.update({
            "name": model_data["name"],
            "description": model_data["description"],
            "context": model_data["context_length"],
            "capabilities": model_data.get("capabilities", []),
            "pricing": {
                "prompt": model_data["pricing"]["input"],
                "completion": model_data["pricing"]["output"]
            },
            "provider": "openai",
            "model": model_data["id"]
        })
        
        # Handle special pricing for non-text models
        if "image_generation" in config["capabilities"]:
            config["pricing"]["image_standard"] = model_data["pricing"]["input"]
            config["pricing"]["image_hd"] = model_data["pricing"]["output"]
            del config["pricing"]["prompt"]
            del config["pricing"]["completion"]
        elif "text_to_speech" in config["capabilities"]:
            config["pricing"]["per_character"] = model_data["pricing"]["input"]
            del config["pricing"]["prompt"]
            del config["pricing"]["completion"]
        elif "speech_recognition" in config["capabilities"]:
            config["pricing"]["per_minute"] = model_data["pricing"]["input"]
            del config["pricing"]["prompt"]
            del config["pricing"]["completion"]
        
        # Preserve manual fields if they exist
        if existing_config:
            for field in ["knowledge", "status", "notes"]:
                if field in existing_config:
                    config[field] = existing_config[field]
        
        return config
    
    async def sync_models(self, dry_run: bool = False) -> Dict:
        """Sync OpenAI models"""
        try:
            models = await self.fetch_models()
            updated_count = 0
            
            for model_data in models:
                model_id = model_data["id"]
                existing_config = self.load_existing_model(model_id)
                new_config = self.create_model_config(model_data, existing_config)
                
                # Check if config changed
                if not existing_config or new_config != existing_config:
                    if not dry_run:
                        model_file = self.models_dir / f"{model_id}.toml"
                        with open(model_file, 'w') as f:
                            tomli_w.dump(new_config, f)
                        print(f"Updated providers/openai/models/{model_id}.toml")
                    updated_count += 1
            
            return {
                "success": True,
                "models_updated": updated_count,
                "total_models": len(models)
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }


async def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Sync OpenAI models")
    parser.add_argument("--dry-run", action="store_true", help="Dry run without writing files")
    
    args = parser.parse_args()
    
    sync = OpenAISync()
    result = await sync.sync_models(dry_run=args.dry_run)
    
    if result["success"]:
        print(f"✅ OpenAI sync completed: {result['models_updated']} models updated")
    else:
        print(f"❌ OpenAI sync failed: {result['error']}")


if __name__ == "__main__":
    asyncio.run(main())