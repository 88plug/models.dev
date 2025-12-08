# AI Provider Sync Automation Documentation

## Overview

The models.dev project now includes a comprehensive sync automation system for managing AI model providers. This system allows for automated synchronization of model configurations from various AI providers.

## Available Sync Tools

### 1. Centralized Sync Manager (`sync_manager.py`)

A Python-based manager that orchestrates synchronization across multiple providers.

**Features:**
- Unified interface for all sync operations
- Status monitoring and reporting
- Dry-run capability for testing
- Error handling and logging

**Usage:**
```bash
# Show sync status
python sync_manager.py --status

# Sync all providers
python sync_manager.py

# Sync specific provider
python sync_manager.py --provider openrouter

# Dry run
python sync_manager.py --provider ollama --dry-run
```

### 2. Shell Script Wrapper (`sync.sh`)

A convenient bash script that handles virtual environment setup and provides a simpler interface.

**Features:**
- Automatic virtual environment management
- Colored output for better readability
- Validation integration
- Help system

**Usage:**
```bash
# Show help
./sync.sh help

# Show status
./sync.sh status

# Sync all providers
./sync.sh sync

# Sync specific provider
./sync.sh sync openrouter

# Dry run
./sync.sh dry-run ollama

# Validate configurations
./sync.sh validate
```

## Supported Providers

### OpenRouter
- **Sync Script**: `sync_openrouter.py`
- **API Source**: OpenRouter public API
- **Models**: 336+ models
- **Features**: Cost tracking, capability detection, manual field preservation

### Ollama
- **Sync Script**: `sync_ollama.py`
- **API Source**: Ollama cloud API (`https://ollama.com/api/tags`)
- **Models**: 20+ models
- **Features**: Free models, capability detection, OpenAI-compatible configuration

## Architecture

### Sync Handler Pattern
Each provider implements a `BaseSyncHandler` with:
- `sync_models()` method for provider-specific logic
- Error handling and result reporting
- Dry-run support

### ProviderSyncManager
Central manager that:
- Maintains registry of sync handlers
- Coordinates multi-provider sync operations
- Provides status monitoring
- Handles error recovery

## Integration Points

### Validation
Sync operations can be followed by configuration validation:
```bash
./sync.sh sync && ./sync.sh validate
```

### Git Integration
Sync manager tracks last sync time using git history for each provider directory.

### Virtual Environment
Automatic Python virtual environment management ensures consistent dependencies.

## Best Practices

1. **Always use dry-run first** to preview changes
2. **Validate configurations** after sync operations
3. **Commit changes** after successful syncs
4. **Monitor provider APIs** for rate limits and changes
5. **Preserve manual fields** during sync operations

## Future Extensibility

The system is designed to easily add new providers:

1. Create provider-specific sync script
2. Implement `BaseSyncHandler` subclass
3. Register handler in `ProviderSyncManager`
4. Update documentation

## Error Handling

- Individual provider failures don't stop other syncs
- Detailed error reporting with context
- Graceful degradation when APIs are unavailable
- Automatic retry logic for transient failures

## Monitoring

Use the status command to monitor:
- Number of models per provider
- Last sync timestamp (git commit)
- Sync handler implementation
- Overall system health