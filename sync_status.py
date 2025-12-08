#!/usr/bin/env python3
"""
Sync Status Generator - Generate structured sync status for dashboard
"""

import json
import tomli
import glob
import os
from datetime import datetime, timezone

def count_models_in_provider(provider_path):
    """Count models in a provider directory"""
    models_path = os.path.join(provider_path, "models")
    if not os.path.exists(models_path):
        return 0
    
    # Count TOML files in models directory
    toml_files = glob.glob(os.path.join(models_path, "*.toml"))
    return len(toml_files)

def get_provider_status(provider_name, provider_path):
    """Get status for a single provider"""
    model_count = count_models_in_provider(provider_path)
    
    # Simple status logic - if models exist, consider synced
    status = "synced" if model_count > 0 else "pending"
    
    return {
        "name": provider_name,
        "model_count": model_count,
        "last_sync": "unknown",  # Would need git history tracking
        "status": status
    }

def generate_sync_status():
    """Generate comprehensive sync status"""
    providers_dir = "providers"
    providers = []
    total_models = 0
    
    # Scan all provider directories
    for provider_name in os.listdir(providers_dir):
        provider_path = os.path.join(providers_dir, provider_name)
        if os.path.isdir(provider_path):
            provider_status = get_provider_status(provider_name, provider_path)
            providers.append(provider_status)
            total_models += provider_status["model_count"]
    
    # Sort providers by name
    providers.sort(key=lambda x: x["name"])
    
    status_data = {
        "last_updated": datetime.now(timezone.utc).isoformat(),
        "total_models": total_models,
        "providers": providers
    }
    
    return status_data

def main():
    """Main function for CLI usage"""
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--status":
        status_data = generate_sync_status()
        print(json.dumps(status_data, indent=2))
    else:
        print("Usage: python sync_status.py --status")
        print("Generates sync status JSON for dashboard")

if __name__ == "__main__":
    main()