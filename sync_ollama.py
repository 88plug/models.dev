#!/usr/bin/env python3
"""
Sync Ollama cloud models with models.dev codebase.

This script fetches the latest models from Ollama's public API and updates the
providers/ollama/models directory with the current model configurations.
"""

import requests
import os
import toml
from datetime import datetime
from pathlib import Path

API_URL = "https://ollama.com/api/tags"
BASE_DIR = Path("providers/ollama/models")

def fetch_models():
    """Fetch models from Ollama API."""
    response = requests.get(API_URL)
    response.raise_for_status()
    data = response.json()
    return data['models']

def create_model_toml(model):
    """Create TOML configuration for an Ollama model."""
    model_name = model['name']
    
    # Extract model name without tags/versions for display
    display_name = model_name.split(':')[0].replace('-', ' ').title()
    
    # Convert size to approximate parameter count
    size_bytes = model['size']
    if size_bytes > 0:
        # Rough approximation: 1B parameters ≈ 2GB
        param_estimate = int(size_bytes / (2 * 1024 * 1024 * 1024))
        if param_estimate > 0:
            display_name += f" {param_estimate}B"
    
    # Parse modification date
    modified_at = model['modified_at']
    release_date = datetime.fromisoformat(modified_at.replace('Z', '+00:00')).strftime("%Y-%m-%d")
    
    # Determine model capabilities based on name patterns
    has_vision = 'vl' in model_name.lower() or 'vision' in model_name.lower()
    has_reasoning = 'thinking' in model_name.lower() or 'reason' in model_name.lower()
    is_coder = 'coder' in model_name.lower() or 'code' in model_name.lower()
    
    # Estimate context limits based on model size
    if size_bytes > 500 * 10**9:  # 500GB+ models
        context_limit = 262144  # 262K tokens
        output_limit = 131072   # 131K tokens
    elif size_bytes > 100 * 10**9:  # 100GB+ models
        context_limit = 131072  # 131K tokens
        output_limit = 65536    # 65K tokens
    else:
        context_limit = 32768   # 32K tokens
        output_limit = 16384    # 16K tokens
    
    # Determine modalities
    input_mods = ['text']
    if has_vision:
        input_mods.append('image')
    
    # All Ollama cloud models are open weights (they're downloadable)
    open_weights = True
    
    # Ollama cloud models are free to use
    cost_data = {
        'input': 0.0,
        'output': 0.0
    }
    
    # Build TOML data
    toml_data = {
        'name': display_name,
        'release_date': release_date,
        'last_updated': datetime.now().strftime("%Y-%m-%d"),
        'attachment': has_vision,  # Vision models support image attachments
        'reasoning': has_reasoning,
        'temperature': True,  # Most models support temperature
        'tool_call': True,    # Most modern models support tool calling
        'open_weights': open_weights,
        'cost': cost_data,
        'limit': {
            'context': context_limit,
            'output': output_limit
        },
        'modalities': {
            'input': input_mods,
            'output': ['text']
        }
    }
    
    return toml_data

def sync_models():
    """Sync models from API to local files."""
    models = fetch_models()
    existing_models = set()
    
    # Create provider directory if it doesn't exist
    BASE_DIR.mkdir(parents=True, exist_ok=True)
    
    # Create/update model files
    for model in models:
        model_name = model['name']
        
        # Skip models with zero size (preview/placeholder models)
        if model['size'] == 0:
            print(f"Skipping zero-size model: {model_name}")
            continue
        
        # Create filename from model name (replace special chars)
        filename = model_name.replace(':', '-').replace('/', '-')
        file_path = BASE_DIR / f"{filename}.toml"
        existing_models.add(str(file_path))
        
        # Read existing file to preserve manually-curated fields
        existing_data = {}
        if file_path.exists():
            try:
                with open(file_path, 'r') as f:
                    existing_data = toml.load(f)
            except Exception as e:
                print(f"Warning: Could not read existing {file_path}: {e}")
        
        # Create new data from API
        toml_data = create_model_toml(model)
        
        # PRESERVE manually-curated fields
        # Only preserve knowledge if it exists and is not empty
        if 'knowledge' in existing_data and existing_data['knowledge']:
            toml_data['knowledge'] = existing_data['knowledge']
        
        # Preserve status field if it exists
        if 'status' in existing_data:
            toml_data['status'] = existing_data['status']
        
        # Write the updated TOML file
        with open(file_path, 'w') as f:
            toml.dump(toml_data, f, encoder=toml.TomlEncoder())
        
        print(f"Updated {file_path}")
    
    # Remove models no longer in API
    for file_path in BASE_DIR.rglob("*.toml"):
        if str(file_path) not in existing_models:
            file_path.unlink()
            print(f"Removed {file_path}")

def create_provider_config():
    """Create the Ollama provider configuration."""
    provider_path = Path("providers/ollama/provider.toml")
    
    provider_data = {
        'name': 'Ollama',
        'env': ['OLLAMA_API_KEY'],
        'npm': '@ai-sdk/openai-compatible',
        'api': 'https://ollama.com/api',
        'doc': 'https://ollama.com/library'
    }
    
    # Create provider directory if it doesn't exist
    provider_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Write provider configuration
    with open(provider_path, 'w') as f:
        toml.dump(provider_data, f, encoder=toml.TomlEncoder())
    
    print(f"Created {provider_path}")

if __name__ == "__main__":
    # Create provider configuration first
    create_provider_config()
    
    # Then sync the models
    sync_models()