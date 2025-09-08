#!/bin/bash

# MoMo SMS Analytics - Quick Demo Setup
# 
# This script sets up the demo environment with sample data

set -e  # Exit on any error

# Configuration
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PYTHON_CMD="${PYTHON_CMD:-python3}"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
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

print_status "🚀 Setting up MoMo SMS Analytics Demo Environment"
print_status "=============================================="

cd "$PROJECT_ROOT"

# Check if Python is available
if ! command -v "$PYTHON_CMD" &> /dev/null; then
    print_error "Python 3 not found. Please install Python 3."
    exit 1
fi

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    print_status "Creating Python virtual environment..."
    "$PYTHON_CMD" -m venv venv
    print_success "Virtual environment created"
fi

# Activate virtual environment
print_status "Activating virtual environment..."
source venv/bin/activate

# Install requirements
print_status "Installing Python dependencies..."
pip install -q -r requirements.txt
print_success "Dependencies installed"

# Generate sample data
print_status "Generating sample transaction data..."
"$PYTHON_CMD" scripts/generate_sample_data.py

# Check if data was generated
if [ -f "data/processed/dashboard.json" ]; then
    print_success "Sample data generated successfully!"
else
    print_error "Failed to generate sample data"
    exit 1
fi

print_status "=============================================="
print_success "🎉 Demo setup complete!"
print_status ""
print_status "Next steps:"
print_status "1. Start the dashboard server:"
print_status "   ./scripts/serve_frontend.sh -o"
print_status ""
print_status "2. Or view analytics in terminal:"
print_status "   python -m etl.run analytics"
print_status ""
print_status "3. Or check system status:"
print_status "   python -m etl.run status"
print_status ""
print_status "Dashboard will be available at: http://localhost:8000"
