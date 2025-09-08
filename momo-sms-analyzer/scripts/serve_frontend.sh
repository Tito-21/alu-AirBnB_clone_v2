#!/bin/bash

# MoMo SMS Analytics - Frontend Server
# 
# This script serves the frontend dashboard using Python's built-in HTTP server
# or optionally with a more advanced server

set -e  # Exit on any error

# Configuration
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DEFAULT_PORT="${FRONTEND_PORT:-8000}"
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

# Function to check if port is available
check_port() {
    local port=$1
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
        return 1  # Port is in use
    else
        return 0  # Port is available
    fi
}

# Function to find available port
find_available_port() {
    local start_port=$1
    local port=$start_port
    
    while [ $port -lt $((start_port + 100)) ]; do
        if check_port $port; then
            echo $port
            return 0
        fi
        port=$((port + 1))
    done
    
    return 1  # No available port found
}

# Function to serve with Python's built-in server
serve_with_python() {
    local port=$1
    
    print_status "Starting Python HTTP server..."
    print_status "Server will be available at: http://localhost:$port"
    print_status "Press Ctrl+C to stop the server"
    print_status "======================================="
    
    cd "$PROJECT_ROOT"
    
    # Try Python 3 first, then Python 2 as fallback
    if command -v python3 >/dev/null 2>&1; then
        python3 -m http.server $port
    elif command -v python >/dev/null 2>&1; then
        python -m SimpleHTTPServer $port
    else
        print_error "Python not found. Please install Python."
        exit 1
    fi
}

# Function to serve with Node.js http-server (if available)
serve_with_node() {
    local port=$1
    
    if command -v npx >/dev/null 2>&1; then
        print_status "Starting Node.js HTTP server..."
        print_status "Server will be available at: http://localhost:$port"
        print_status "Press Ctrl+C to stop the server"
        print_status "======================================="
        
        cd "$PROJECT_ROOT"
        npx http-server -p $port -c-1 --cors
    else
        print_warning "Node.js/npx not found. Falling back to Python server."
        serve_with_python $port
    fi
}

# Function to check dashboard data
check_dashboard_data() {
    local dashboard_file="$PROJECT_ROOT/data/processed/dashboard.json"
    
    if [ ! -f "$dashboard_file" ]; then
        print_warning "Dashboard data not found at: $dashboard_file"
        print_status "You may need to run the ETL pipeline first:"
        print_status "  ./scripts/run_etl.sh"
        print_status ""
        print_status "Continuing to serve frontend anyway..."
        return 1
    else
        print_success "Dashboard data found at: $dashboard_file"
        return 0
    fi
}

# Function to open browser (optional)
open_browser() {
    local url=$1
    
    if command -v open >/dev/null 2>&1; then
        # macOS
        open "$url"
    elif command -v xdg-open >/dev/null 2>&1; then
        # Linux
        xdg-open "$url"
    elif command -v start >/dev/null 2>&1; then
        # Windows
        start "$url"
    else
        print_status "Browser not auto-opened. Please visit: $url"
    fi
}

# Function to show usage
show_usage() {
    echo "MoMo SMS Analytics - Frontend Server"
    echo ""
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  -p, --port PORT     Port to serve on (default: $DEFAULT_PORT)"
    echo "  -n, --node         Use Node.js http-server instead of Python"
    echo "  -o, --open         Open browser automatically"
    echo "  -h, --help         Show this help message"
    echo ""
    echo "Environment Variables:"
    echo "  FRONTEND_PORT      Default port (default: 8000)"
    echo "  PYTHON_CMD         Python command to use (default: python3)"
    echo ""
    echo "Examples:"
    echo "  $0                 # Serve on default port"
    echo "  $0 -p 3000         # Serve on port 3000"
    echo "  $0 -n -o           # Use Node.js server and open browser"
    echo ""
}

# Main execution
main() {
    local port=$DEFAULT_PORT
    local use_node=false
    local open_browser_flag=false
    
    # Parse command line arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            -p|--port)
                port="$2"
                shift 2
                ;;
            -n|--node)
                use_node=true
                shift
                ;;
            -o|--open)
                open_browser_flag=true
                shift
                ;;
            -h|--help)
                show_usage
                exit 0
                ;;
            *)
                print_error "Unknown option: $1"
                show_usage
                exit 1
                ;;
        esac
    done
    
    # Validate port number
    if ! [[ "$port" =~ ^[0-9]+$ ]] || [ "$port" -lt 1 ] || [ "$port" -gt 65535 ]; then
        print_error "Invalid port number: $port"
        exit 1
    fi
    
    print_status "MoMo SMS Analytics - Frontend Server"
    print_status "====================================="
    
    # Check if dashboard data exists
    check_dashboard_data
    
    # Check if requested port is available
    if ! check_port $port; then
        print_warning "Port $port is already in use."
        
        # Try to find an available port
        available_port=$(find_available_port $port)
        if [ $? -eq 0 ]; then
            print_status "Using available port: $available_port"
            port=$available_port
        else
            print_error "No available ports found starting from $port"
            exit 1
        fi
    fi
    
    # Prepare server URL
    local server_url="http://localhost:$port"
    
    # Open browser if requested
    if [ "$open_browser_flag" = true ]; then
        print_status "Opening browser in 3 seconds..."
        (sleep 3 && open_browser "$server_url") &
    fi
    
    # Start the appropriate server
    if [ "$use_node" = true ]; then
        serve_with_node $port
    else
        serve_with_python $port
    fi
}

# Cleanup function for graceful shutdown
cleanup() {
    print_status ""
    print_status "Shutting down server..."
    exit 0
}

# Set up cleanup trap
trap cleanup SIGINT SIGTERM

# Check if script is being sourced or executed
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi
