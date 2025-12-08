#!/usr/bin/env python3
"""
Anthropic API Sync for models.dev
Fetches latest models from Anthropic API
"""

import asyncio
import aiohttp
import tomli
import tomli_w
from pathlib import Path
from typing import Dict, List, Optional
import os


class AnthropicSync:
    """Sync handler for Anthropic models"""
    
    def __init__(self, providers_dir: str = "providers"):
        self.providers_dir = Path(providers_dir)
        self.provider_name = "anthropic"
        self.models_dir = self.providers_dir / self.provider_name / "models"
        self.models_dir.mkdir(parents=True, exist_ok=True)
    
    async def fetch_models(self) -> List[Dict]:
        """Fetch available models from Anthropic API"""
        # Anthropic doesn't have a public models API, so we'll use known models
        # This list can be updated as Anthropic releases new models
        
        known_models = [
            {
                "id": "claude-3-5-sonnet-20241022",
                "name": "Claude 3.5 Sonnet",
                "description": "Anthropic's most intelligent model, balancing capability, speed, and cost",
                "context_length": 200000,
                "capabilities": ["reasoning", "coding", "vision"],
                "pricing": {
                    "input": 3.00,  # $3.00 per million tokens
                    "output": 15.00  # $15.00 per million tokens
                }
            },
            {
                "id": "claude-3-5-haiku-20241022", 
                "name": "Claude 3.5 Haiku",
                "description": "Anthropic's fastest and most compact model",
                "context_length": 200000,
                "capabilities": ["reasoning", "coding"],
                "pricing": {
                    "input": 0.80,  # $0.80 per million tokens
                    "output": 4.00   # $4.00 per million tokens
                }
            },
            {
                "id": "claude-3-opus-20240229",
                "name": "Claude 3 Opus",
                "description": "Anthropic's most powerful model for highly complex tasks",
                "context_length": 200000,
                "capabilities": ["reasoning", "coding", "vision"],
                "pricing": {
                    "input": 15.00,  # $15.00 per million tokens
                    "output": 75.00   # $75.00 per million tokens
                }
            },
            {
                "id": "claude-3-sonnet-20240229",
                "name": "Claude 3 Sonnet",
                "description": "Balanced model between intelligence and speed",
                "context_length": 200000,
                "capabilities": ["reasoning", "coding", "vision"],
                "pricing": {
                    "input": 3.00,  # $3.00 per million tokens
                    "output": 15.00  # $15.00 per million tokens
                }
            },
            {
                "id": "claude-3-haiku-20240307",
                "name": "Claude 3 Haiku",
                "description": "Fastest and most cost-effective model",
                "context_length": 200000,
                "capabilities": ["reasoning", "coding", "vision"],
                "pricing": {
                    "input": 0.25,  # $0.25 per million tokens
                    "output": 1.25   # $1.25 per million tokens
                }
            },
            {
                "id": "claude-2.1",
                "name": "Claude 2.1",
                "description": "Previous generation model with 200K context",
                "context_length": 200000,
                "capabilities": ["reasoning", "coding"],
                "pricing": {
                    "input": 8.00,   # $8.00 per million tokens
                    "output": 24.00   # $24.00 per million tokens
                }
            },
            {
                "id": "claude-2.0",
                "name": "Claude 2.0",
                "description": "Previous generation model",
                "context_length": 100000,
                "capabilities": ["reasoning", "coding"],
                "pricing": {
                    "input": 8.00,   # $8.00 per million tokens
                    "output": 24.00   # $24.00 per million tokens
                }
            },
            {
                "id": "claude-instant-1.2",
                "name": "Claude Instant 1.2",
                "description": "Fast, lightweight model for simple tasks",
                "context_length": 100000,
                "capabilities": ["reasoning", "coding"],
                "pricing": {
                    "input": 0.80,   # $0.80 per million tokens
                    "output": 2.40    # $2.40 per million tokens
                }
            }
        ]
        
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
            "provider": "anthropic",
            "model": model_data["id"]
        })
        
        # Preserve manual fields if they exist
        if existing_config:
            for field in ["knowledge", "status", "notes"]:
                if field in existing_config:
                    config[field] = existing_config[field]
        
        return config
    
    async def sync_models(self, dry_run: bool = False) -> Dict:
        """Sync Anthropic models"""
        try:
            models = await self.fetch_models()
            updated_count = 0
            updated_models = []
            
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
                        print(f"Updated providers/anthropic/models/{model_id}.toml")
                    updated_count += 1
                    updated_models.append(model_id)
            
            return {
                "success": True,
                "models_updated": updated_count,
                "updated_models": updated_models,
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
    
    parser = argparse.ArgumentParser(description="Sync Anthropic models")
    parser.add_argument("--dry-run", action="store_true", help="Dry run without writing files")
    
    args = parser.parse_args()
    
    sync = AnthropicSync()
    result = await sync.sync_models(dry_run=args.dry_run)
    
    if result["success"]:
        print(f"✅ Anthropic sync completed: {result['models_updated']} models updated")
        if result['models_updated'] > 0:
            print("Updated models:")
            for model in result.get('updated_models', []):
                print(f"  - {model}")
    else:
        print(f"❌ Anthropic sync failed: {result['error']}")


if __name__ == "__main__":
    asyncio.run(main())