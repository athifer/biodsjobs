#!/bin/bash

# BioDSJobs Deployment Script
# This script sets up and deploys the BioDSJobs platform

set -e

echo "🚀 BioDSJobs Deployment Script"
echo "==============================="

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

# Check if Python is installed
check_python() {
    print_status "Checking Python installation..."
    if command -v python3 &> /dev/null; then
        PYTHON_VERSION=$(python3 --version | cut -d " " -f 2)
        print_success "Python $PYTHON_VERSION found"
    else
        print_error "Python 3 is not installed. Please install Python 3.8+ and try again."
        exit 1
    fi
}

# Check if we're in the right directory
check_directory() {
    if [ ! -f "backend/app.py" ] || [ ! -f "frontend/index.html" ]; then
        print_error "Please run this script from the biodsjobs root directory"
        exit 1
    fi
    print_success "Directory structure verified"
}

# Create virtual environment
setup_venv() {
    print_status "Setting up virtual environment..."
    
    if [ ! -d ".venv" ]; then
        python3 -m venv .venv
        print_success "Virtual environment created"
    else
        print_warning "Virtual environment already exists"
    fi
    
    # Activate virtual environment
    source .venv/bin/activate
    print_success "Virtual environment activated"
}

# Install dependencies
install_dependencies() {
    print_status "Installing Python dependencies..."
    pip install --upgrade pip
    pip install -r backend/requirements.txt
    print_success "Dependencies installed"
}

# Initialize database
init_database() {
    print_status "Initializing database..."
    cd backend
    python -c "from db import init_db; init_db(); print('Database initialized successfully')"
    cd ..
    print_success "Database setup complete"
}

# Run initial job ingestion
initial_ingestion() {
    print_status "Running initial job ingestion (this may take a few minutes)..."
    cd backend
    
    # Run ingestion with better error handling
    if python ingestor.py > /tmp/ingestion.log 2>&1; then
        # Get job count if ingestion was successful
        JOB_COUNT=$(python -c "from db import get_session, Job; session = get_session(); count = session.query(Job).count(); session.close(); print(count)" 2>/dev/null || echo "0")
        print_success "Initial ingestion complete - $JOB_COUNT jobs loaded"
    else
        print_warning "Job ingestion completed with some errors (check logs for details)"
        JOB_COUNT=$(python -c "from db import get_session, Job; session = get_session(); count = session.query(Job).count(); session.close(); print(count)" 2>/dev/null || echo "0")
        print_status "Current job count: $JOB_COUNT jobs"
    fi
    
    cd ..
}

# Test the server
test_server() {
    print_status "Testing server startup..."
    cd backend
    timeout 10s python start_server.py > /dev/null 2>&1 &
    SERVER_PID=$!
    sleep 3
    
    if kill -0 $SERVER_PID 2>/dev/null; then
        print_success "Server started successfully"
        kill $SERVER_PID 2>/dev/null || true
    else
        print_warning "Server test inconclusive"
    fi
    cd ..
}

# Production deployment setup
setup_production() {
    print_status "Setting up production configuration..."
    
    # Install production server
    pip install gunicorn
    
    # Create production startup script
    cat > start_production.sh << 'EOF'
#!/bin/bash
cd backend
source ../.venv/bin/activate
exec gunicorn -w 4 -k uvicorn.workers.UvicornWorker app:app --bind 0.0.0.0:8000
EOF
    
    chmod +x start_production.sh
    print_success "Production setup complete"
}

# Create systemd service (Linux only)
create_service() {
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        print_status "Creating systemd service..."
        
        CURRENT_DIR=$(pwd)
        USER=$(whoami)
        
        cat > biodsjobs.service << EOF
[Unit]
Description=BioDSJobs Platform
After=network.target

[Service]
Type=exec
User=$USER
WorkingDirectory=$CURRENT_DIR
ExecStart=$CURRENT_DIR/start_production.sh
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF
        
        print_success "Systemd service file created: biodsjobs.service"
        print_status "To install: sudo cp biodsjobs.service /etc/systemd/system/"
        print_status "To start: sudo systemctl start biodsjobs"
        print_status "To enable on boot: sudo systemctl enable biodsjobs"
    fi
}

# Main deployment function
main() {
    echo
    print_status "Starting BioDSJobs deployment..."
    echo
    
    check_python
    check_directory
    setup_venv
    install_dependencies
    init_database
    initial_ingestion
    test_server
    
    echo
    print_status "Would you like to set up production configuration? (y/n)"
    read -r response
    if [[ "$response" =~ ^([yY][eE][sS]|[yY])$ ]]; then
        setup_production
        create_service
    fi
    
    echo
    print_success "🎉 Deployment complete!"
    echo
    echo "Next steps:"
    echo "1. Start the server: cd backend && python start_server.py"
    echo "2. Access the application: http://localhost:8000"
    echo "3. View API documentation: http://localhost:8000/docs"
    echo
    echo "For production deployment:"
    echo "1. Use: ./start_production.sh"
    echo "2. Or install as system service (Linux)"
    echo
}

# Handle script arguments
case "${1:-}" in
    --help|-h)
        echo "BioDSJobs Deployment Script"
        echo
        echo "Usage: $0 [options]"
        echo
        echo "Options:"
        echo "  --help, -h     Show this help message"
        echo "  --prod         Setup production configuration only"
        echo "  --dev          Setup development environment only"
        echo
        exit 0
        ;;
    --prod)
        setup_production
        create_service
        exit 0
        ;;
    --dev)
        check_python
        check_directory
        setup_venv
        install_dependencies
        init_database
        print_success "Development environment ready!"
        exit 0
        ;;
    *)
        main
        ;;
esac
