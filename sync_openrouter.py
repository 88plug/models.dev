#!/usr/bin/env python3
"""
Sync OpenRouter models with models.dev codebase.

This script fetches the latest models from OpenRouter API and updates the
providers/openrouter/models directory with the current model configurations.
"""

import requests
import os
import toml
from datetime import datetime
from pathlib import Path

API_URL = "https://openrouter.ai/api/v1/models"
BASE_DIR = Path("providers/openrouter/models")

def fetch_models():
    """Fetch models from OpenRouter API."""
    response = requests.get(API_URL)
    response.raise_for_status()
    data = response.json()
    return data['data']

def create_model_toml(model):
    """Create TOML configuration for a model."""
    model_id = model['id']
    name = model['name']
    pricing = model['pricing']
    context_length = model['context_length']

    # Determine modalities (filter to schema-allowed values)
    architecture = model.get('architecture', {})
    ALLOWED_MODALITIES = ['text', 'audio', 'image', 'video', 'pdf']
    raw_input_mods = architecture.get('input_modalities', [])
    raw_output_mods = architecture.get('output_modalities', [])

    # Filter to only allowed modalities (file handled via attachment field)
    input_mods = [m for m in raw_input_mods if m in ALLOWED_MODALITIES]
    output_mods = [m for m in raw_output_mods if m in ALLOWED_MODALITIES]

    # Supported parameters
    supported_params = model.get('supported_parameters', [])
    has_temperature = 'temperature' in supported_params
    has_tools = 'tools' in supported_params
    has_reasoning = 'reasoning' in supported_params or 'include_reasoning' in supported_params

    # Max completion tokens
    max_completion = model.get('top_provider', {}).get('max_completion_tokens')
    if not max_completion:
        max_completion = model.get('max_completion_tokens', 4096)

    # Check if open weights (has hugging face ID and is free)
    hf_id = model.get('hugging_face_id', '') or ''
    has_hf_id = bool(hf_id.strip())
    is_free = pricing['prompt'] == '0' and pricing['completion'] == '0'
    is_open_weights = has_hf_id and is_free

    # Build TOML data
    release_date = datetime.fromtimestamp(model['created']).strftime("%Y-%m-%d")

    # Attachment support (image or file input)
    attachment = 'image' in raw_input_mods or 'file' in raw_input_mods

    # Cost data with optional cache pricing (convert strings to floats for schema)
    # Note: -1 indicates dynamic pricing, convert to 0 to satisfy schema constraints
    input_price = float(pricing['prompt'])
    output_price = float(pricing['completion'])
    cost_data = {
        'input': max(0, input_price),  # Convert -1 (dynamic) to 0
        'output': max(0, output_price)  # Convert -1 (dynamic) to 0
    }
    if 'input_cache_read' in pricing and pricing['input_cache_read'] != '0':
        cache_read = float(pricing['input_cache_read'])
        cost_data['cache_read'] = max(0, cache_read)
    if 'input_cache_write' in pricing and pricing['input_cache_write'] != '0':
        cache_write = float(pricing['input_cache_write'])
        cost_data['cache_write'] = max(0, cache_write)

    toml_data = {
        'id': model_id,
        'name': name,
        'release_date': release_date,
        'last_updated': datetime.now().strftime("%Y-%m-%d"),
        'attachment': attachment,
        'reasoning': has_reasoning,
        'temperature': has_temperature,
        'tool_call': has_tools,
        'open_weights': is_open_weights,
        'cost': cost_data,
        'limit': {
            'context': context_length,
            'output': max_completion
        },
        'modalities': {
            'input': input_mods,
            'output': output_mods
        }
    }

    return toml_data

def sync_models():
    """Sync models from API to local files."""
    models = fetch_models()
    existing_models = set()

    # Create/update model files
    for model in models:
        model_id = model['id']
        provider, model_name = model_id.split('/', 1)

        provider_dir = BASE_DIR / provider
        provider_dir.mkdir(parents=True, exist_ok=True)

        file_path = provider_dir / f"{model_name}.toml"
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

        # PRESERVE manually-curated fields (grandfather them)
        PRESERVE_FIELDS = ['knowledge', 'status']
        for field in PRESERVE_FIELDS:
            if field in existing_data:
                toml_data[field] = existing_data[field]

        # PRESERVE cost subfields not provided by API
        if 'cost' in existing_data:
            PRESERVE_COST_FIELDS = ['reasoning', 'input_audio', 'output_audio', 'cache_write', 'cache_read']
            for cost_field in PRESERVE_COST_FIELDS:
                if cost_field in existing_data['cost']:
                    # Only preserve if not already set by API
                    if cost_field not in toml_data.get('cost', {}):
                        toml_data['cost'][cost_field] = existing_data['cost'][cost_field]

        with open(file_path, 'w') as f:
            toml.dump(toml_data, f, encoder=toml.TomlEncoder())

        print(f"Updated {file_path}")

    # Remove models no longer in API
    for file_path in BASE_DIR.rglob("*.toml"):
        if str(file_path) not in existing_models:
            file_path.unlink()
            print(f"Removed {file_path}")

if __name__ == "__main__":
    sync_models()