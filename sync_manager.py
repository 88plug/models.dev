#!/usr/bin/env python3
"""
Centralized AI Provider Sync Manager for models.dev
Handles automated synchronization of multiple AI model providers
"""

import asyncio
import json
import os
import sys
from pathlib import Path
from typing import Dict, List, Optional
import aiohttp
import tomli
import tomli_w

# Add current directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))


class BaseSyncHandler:
    """Base class for provider sync handlers"""
    
    def __init__(self, providers_dir: str = "providers"):
        self.providers_dir = Path(providers_dir)
    
    async def sync_models(self, dry_run: bool = False) -> Dict:
        """Sync models for this provider"""
        raise NotImplementedError("Subclasses must implement sync_models")


class OpenRouterSync(BaseSyncHandler):
    """OpenRouter sync handler"""
    
    async def sync_models(self, dry_run: bool = False) -> Dict:
        """Sync OpenRouter models by running the existing script"""
        import subprocess
        
        try:
            result = subprocess.run(
                [sys.executable, "sync_openrouter.py"],
                capture_output=True, text=True
            )
            
            if result.returncode == 0:
                # Count updated models from output
                lines = result.stdout.strip().split('\n')
                updated_count = len([line for line in lines if line.startswith("Updated providers/")])
                
                return {
                    "success": True,
                    "models_updated": updated_count,
                    "output": result.stdout
                }
            else:
                return {
                    "success": False,
                    "error": result.stderr,
                    "output": result.stdout
                }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }


class OllamaSync(BaseSyncHandler):
    """Ollama sync handler"""
    
    async def sync_models(self, dry_run: bool = False) -> Dict:
        """Sync Ollama models by running the existing script"""
        import subprocess
        
        try:
            result = subprocess.run(
                [sys.executable, "sync_ollama.py"],
                capture_output=True, text=True
            )
            
            if result.returncode == 0:
                # Count updated models from output
                lines = result.stdout.strip().split('\n')
                updated_count = len([line for line in lines if line.startswith("Updated providers/")])
                
                return {
                    "success": True,
                    "models_updated": updated_count,
                    "output": result.stdout
                }
            else:
                return {
                    "success": False,
                    "error": result.stderr,
                    "output": result.stdout
                }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }


class AnthropicSync(BaseSyncHandler):
    """Anthropic sync handler"""
    
    async def sync_models(self, dry_run: bool = False) -> Dict:
        """Sync Anthropic models by running the existing script"""
        import subprocess
        
        try:
            result = subprocess.run(
                [sys.executable, "sync_anthropic.py"],
                capture_output=True, text=True
            )
            
            if result.returncode == 0:
                # Count updated models from output
                lines = result.stdout.strip().split('\n')
                updated_count = len([line for line in lines if line.startswith("Updated providers/")])
                
                return {
                    "success": True,
                    "models_updated": updated_count,
                    "output": result.stdout
                }
            else:
                return {
                    "success": False,
                    "error": result.stderr,
                    "output": result.stdout
                }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }


class OpenAISync(BaseSyncHandler):
    """OpenAI sync handler"""
    
    async def sync_models(self, dry_run: bool = False) -> Dict:
        """Sync OpenAI models by running the existing script"""
        import subprocess
        
        try:
            result = subprocess.run(
                [sys.executable, "sync_openai.py"],
                capture_output=True, text=True
            )
            
            if result.returncode == 0:
                # Count updated models from output
                lines = result.stdout.strip().split('\n')
                updated_count = len([line for line in lines if line.startswith("Updated providers/")])
                
                return {
                    "success": True,
                    "models_updated": updated_count,
                    "output": result.stdout
                }
            else:
                return {
                    "success": False,
                    "error": result.stderr,
                    "output": result.stdout
                }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }


class ProviderSyncManager:
    """Manages synchronization of multiple AI model providers"""
    
    def __init__(self, providers_dir: str = "providers"):
        self.providers_dir = Path(providers_dir)
        self.sync_handlers = {
            "openrouter": OpenRouterSync(providers_dir),
            "ollama": OllamaSync(providers_dir),
            "anthropic": AnthropicSync(providers_dir),
            "openai": OpenAISync(providers_dir)
        }
    
    async def sync_all_providers(self, dry_run: bool = False) -> Dict[str, Dict]:
        """Sync all available providers"""
        results = {}
        
        for provider_name, handler in self.sync_handlers.items():
            print(f"\n🔄 Syncing {provider_name}...")
            try:
                result = await handler.sync_models(dry_run=dry_run)
                results[provider_name] = result
                if result.get("success"):
                    print(f"✅ {provider_name}: {result.get('models_updated', 0)} models updated")
                else:
                    print(f"❌ {provider_name}: Error - {result.get('error', 'Unknown error')}")
            except Exception as e:
                print(f"❌ {provider_name}: Error - {e}")
                results[provider_name] = {"error": str(e)}
        
        return results
    
    async def sync_single_provider(self, provider_name: str, dry_run: bool = False) -> Dict:
        """Sync a specific provider"""
        if provider_name not in self.sync_handlers:
            return {"error": f"Provider '{provider_name}' not supported"}
        
        handler = self.sync_handlers[provider_name]
        return await handler.sync_models(dry_run=dry_run)
    
    def get_available_providers(self) -> List[str]:
        """Get list of available providers with sync support"""
        return list(self.sync_handlers.keys())
    
    def get_sync_status(self) -> Dict[str, Dict]:
        """Get current sync status for all providers"""
        status = {}
        
        for provider_name, handler in self.sync_handlers.items():
            provider_dir = self.providers_dir / provider_name
            model_files = list(provider_dir.glob("models/*.toml"))
            
            status[provider_name] = {
                "models_count": len(model_files),
                "last_sync": self._get_last_sync_time(provider_name),
                "sync_handler": handler.__class__.__name__
            }
        
        return status
    
    def _get_last_sync_time(self, provider_name: str) -> Optional[str]:
        """Get last sync time from git history"""
        try:
            import subprocess
            result = subprocess.run(
                ["git", "log", "--oneline", "-1", "--", f"providers/{provider_name}/"],
                capture_output=True, text=True
            )
            if result.returncode == 0 and result.stdout:
                return result.stdout.split()[0]  # Return commit hash
        except:
            pass
        return None


async def main():
    """Main entry point for sync manager"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Sync AI model providers")
    parser.add_argument("--provider", help="Sync specific provider")
    parser.add_argument("--dry-run", action="store_true", help="Dry run without writing files")
    parser.add_argument("--status", action="store_true", help="Show sync status")
    
    args = parser.parse_args()
    
    manager = ProviderSyncManager()
    
    if args.status:
        status = manager.get_sync_status()
        print("\n📊 Sync Status:")
        for provider, info in status.items():
            print(f"  {provider}: {info['models_count']} models, last sync: {info['last_sync'] or 'unknown'}")
        return
    
    if args.provider:
        result = await manager.sync_single_provider(args.provider, args.dry_run)
        print(f"\n📋 {args.provider} Sync Result:")
        print(json.dumps(result, indent=2))
    else:
        results = await manager.sync_all_providers(args.dry_run)
        print(f"\n📋 All Providers Sync Results:")
        print(json.dumps(results, indent=2))


if __name__ == "__main__":
    asyncio.run(main())