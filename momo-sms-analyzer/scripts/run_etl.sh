#!/bin/bash

# MoMo SMS Analytics - ETL Pipeline Runner
# 
# This script runs the complete ETL pipeline:
# 1. Parse XML data
# 2. Clean and normalize
# 3. Categorize transactions
# 4. Load to database
# 5. Export dashboard JSON

set -e  # Exit on any error

# Configuration
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PYTHON_CMD="${PYTHON_CMD:-python3}"
VENV_PATH="${PROJECT_ROOT}/venv"

# Default paths (can be overridden by environment variables)
XML_INPUT="${XML_INPUT:-${PROJECT_ROOT}/data/raw/momo.xml}"
DASHBOARD_OUTPUT="${DASHBOARD_OUTPUT:-${PROJECT_ROOT}/data/processed/dashboard.json}"

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

# Function to check if virtual environment exists and activate it
setup_environment() {
    print_status "Setting up Python environment..."
    
    # Check if virtual environment exists
    if [ -d "$VENV_PATH" ]; then
        print_status "Activating virtual environment..."
        source "$VENV_PATH/bin/activate"
    else
        print_warning "Virtual environment not found at $VENV_PATH"
        print_status "Please create a virtual environment with: python3 -m venv venv"
        print_status "Then activate it and install requirements: pip install -r requirements.txt"
    fi
    
    # Change to project directory
    cd "$PROJECT_ROOT"
}

# Function to check prerequisites
check_prerequisites() {
    print_status "Checking prerequisites..."
    
    # Check if Python is available
    if ! command -v "$PYTHON_CMD" &> /dev/null; then
        print_error "Python 3 not found. Please install Python 3."
        exit 1
    fi
    
    # Check if input XML file exists (only if running full pipeline)
    if [ "$1" = "full" ] && [ ! -f "$XML_INPUT" ]; then
        print_warning "Input XML file not found at: $XML_INPUT"
        print_status "You can specify a different path with: XML_INPUT=/path/to/file.xml $0"
        print_status "For now, we'll skip the XML parsing step."
        SKIP_XML=true
    fi
    
    # Create necessary directories
    mkdir -p "${PROJECT_ROOT}/data/raw"
    mkdir -p "${PROJECT_ROOT}/data/processed"
    mkdir -p "${PROJECT_ROOT}/data/logs"
    mkdir -p "${PROJECT_ROOT}/data/logs/dead_letter"
}

# Function to run the ETL pipeline
run_etl_pipeline() {
    print_status "Starting MoMo SMS ETL Pipeline..."
    print_status "================================="
    
    if [ "$SKIP_XML" != "true" ]; then
        print_status "Input XML: $XML_INPUT"
    else
        print_warning "Skipping XML parsing - no input file specified"
    fi
    print_status "Output Dashboard: $DASHBOARD_OUTPUT"
    print_status "================================="
    
    # Run the ETL pipeline using the Python CLI
    if [ "$SKIP_XML" != "true" ]; then
        print_status "Running full ETL pipeline..."
        "$PYTHON_CMD" -m etl.run run-full-pipeline --xml-file "$XML_INPUT" --output-json "$DASHBOARD_OUTPUT"
    else
        print_status "Running export-only (using existing database data)..."
        "$PYTHON_CMD" -m etl.run export-only --output-json "$DASHBOARD_OUTPUT"
    fi
    
    if [ $? -eq 0 ]; then
        print_success "ETL pipeline completed successfully!"
        print_status "Dashboard data exported to: $DASHBOARD_OUTPUT"
    else
        print_error "ETL pipeline failed!"
        exit 1
    fi
}

# Function to show system status
show_status() {
    print_status "Checking MoMo SMS ETL System Status..."
    "$PYTHON_CMD" -m etl.run status
}

# Function to show analytics
show_analytics() {
    print_status "Generating MoMo SMS Analytics..."
    "$PYTHON_CMD" -m etl.run analytics
}

# Function to show usage
show_usage() {
    echo "MoMo SMS Analytics - ETL Pipeline Runner"
    echo ""
    echo "Usage: $0 [COMMAND] [OPTIONS]"
    echo ""
    echo "Commands:"
    echo "  full        Run the complete ETL pipeline (default)"
    echo "  export      Export dashboard data only (skip XML processing)"
    echo "  status      Show system status"
    echo "  analytics   Show transaction analytics"
    echo "  help        Show this help message"
    echo ""
    echo "Environment Variables:"
    echo "  XML_INPUT              Path to input XML file (default: data/raw/momo.xml)"
    echo "  DASHBOARD_OUTPUT       Path to output JSON file (default: data/processed/dashboard.json)"
    echo "  PYTHON_CMD            Python command to use (default: python3)"
    echo ""
    echo "Examples:"
    echo "  $0                                    # Run full pipeline with defaults"
    echo "  $0 full                              # Run full pipeline"
    echo "  $0 export                            # Export dashboard data only"
    echo "  $0 status                            # Check system status"
    echo "  XML_INPUT=/path/to/data.xml $0       # Use custom XML file"
    echo ""
}

# Main execution
main() {
    local command="${1:-full}"
    
    case "$command" in
        "full")
            setup_environment
            check_prerequisites "full"
            run_etl_pipeline
            ;;
        "export")
            setup_environment
            check_prerequisites "export"
            print_status "Exporting dashboard data only..."
            "$PYTHON_CMD" -m etl.run export-only --output-json "$DASHBOARD_OUTPUT"
            if [ $? -eq 0 ]; then
                print_success "Dashboard data exported successfully!"
            else
                print_error "Export failed!"
                exit 1
            fi
            ;;
        "status")
            setup_environment
            show_status
            ;;
        "analytics")
            setup_environment
            show_analytics
            ;;
        "help"|"-h"|"--help")
            show_usage
            ;;
        *)
            print_error "Unknown command: $command"
            echo ""
            show_usage
            exit 1
            ;;
    esac
}

# Check if script is being sourced or executed
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi
