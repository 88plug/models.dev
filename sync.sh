#!/usr/bin/env bash

# AI Provider Sync Automation Script for models.dev
# Centralized script to manage all provider sync operations

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[SYNC]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check if virtual environment exists
check_venv() {
    if [ ! -d "venv" ]; then
        print_status "Creating virtual environment..."
        python -m venv venv
    fi
    
    print_status "Activating virtual environment..."
    source venv/bin/activate
    
    # Install required packages
    if ! pip show tomli tomli-w aiohttp > /dev/null 2>&1; then
        print_status "Installing required packages..."
        pip install tomli tomli-w aiohttp
    fi
}

# Function to show sync status
show_status() {
    print_status "Checking sync status..."
    python sync_manager.py --status
}

# Function to sync all providers
sync_all() {
    print_status "Syncing all providers..."
    python sync_manager.py
}

# Function to sync specific provider
sync_provider() {
    local provider=$1
    print_status "Syncing provider: $provider"
    python sync_manager.py --provider "$provider"
}

# Function to run dry run
dry_run() {
    local provider=$1
    if [ -n "$provider" ]; then
        print_status "Dry run for provider: $provider"
        python sync_manager.py --provider "$provider" --dry-run
    else
        print_status "Dry run for all providers"
        python sync_manager.py --dry-run
    fi
}

# Function to validate configurations
validate_configs() {
    print_status "Validating configurations..."
    if command -v bun > /dev/null 2>&1; then
        bun validate
    else
        print_warning "Bun not found, skipping validation"
    fi
}

# Function to show help
show_help() {
    echo "Usage: $0 [OPTION]"
    echo ""
    echo "Options:"
    echo "  status                    Show sync status for all providers"
    echo "  sync [provider]           Sync all providers or specific provider"
    echo "  dry-run [provider]        Dry run sync without writing files"
    echo "  validate                  Validate configurations after sync"
    echo "  help                      Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 status                 Show current sync status"
    echo "  $0 sync                   Sync all providers"
    echo "  $0 sync openrouter        Sync only OpenRouter"
    echo "  $0 dry-run ollama         Dry run Ollama sync"
    echo "  $0 validate               Validate configurations"
}

# Main script logic
main() {
    # Check if we're in the correct directory
    if [ ! -f "sync_manager.py" ]; then
        print_error "Must be run from the project root directory"
        exit 1
    fi
    
    # Setup virtual environment
    check_venv
    
    case "${1:-}" in
        "status")
            show_status
            ;;
        "sync")
            if [ -n "$2" ]; then
                sync_provider "$2"
            else
                sync_all
            fi
            ;;
        "dry-run")
            dry_run "$2"
            ;;
        "validate")
            validate_configs
            ;;
        "help"|"--help"|"-h")
            show_help
            ;;
        "")
            show_help
            ;;
        *)
            print_error "Unknown option: $1"
            show_help
            exit 1
            ;;
    esac
}

# Run main function with all arguments
main "$@"