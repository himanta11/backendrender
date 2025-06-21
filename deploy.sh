#!/bin/bash

# Deployment script for Aspirant application
set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Docker is installed
check_docker() {
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed. Please install Docker first."
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        print_error "Docker Compose is not installed. Please install Docker Compose first."
        exit 1
    fi
}

# Build and deploy with Docker Compose
deploy_docker() {
    print_status "Building and deploying with Docker Compose..."
    
    # Stop existing containers
    docker-compose down
    
    # Build and start services
    docker-compose up --build -d
    
    print_status "Deployment completed successfully!"
    print_status "Application is running at: http://localhost"
    print_status "API is available at: http://localhost/api"
    print_status "Health check: http://localhost/health"
}

# Deploy to production (example for cloud platforms)
deploy_production() {
    print_status "Deploying to production..."
    
    # Build production image
    docker build -t aspirant-app:latest .
    
    # Tag for registry (replace with your registry)
    # docker tag aspirant-app:latest your-registry/aspirant-app:latest
    # docker push your-registry/aspirant-app:latest
    
    print_status "Production image built successfully!"
    print_warning "Please configure your production environment variables and deploy to your preferred platform."
}

# Deploy to specific platform
deploy_platform() {
    case $1 in
        "docker")
            deploy_docker
            ;;
        "production")
            deploy_production
            ;;
        "heroku")
            deploy_heroku
            ;;
        "railway")
            deploy_railway
            ;;
        *)
            print_error "Unknown platform: $1"
            print_status "Available platforms: docker, production, heroku, railway"
            exit 1
            ;;
    esac
}

# Deploy to Heroku (example)
deploy_heroku() {
    print_status "Deploying to Heroku..."
    
    # Check if Heroku CLI is installed
    if ! command -v heroku &> /dev/null; then
        print_error "Heroku CLI is not installed. Please install it first."
        exit 1
    fi
    
    # Create Heroku app if it doesn't exist
    # heroku create your-app-name
    
    # Set environment variables
    # heroku config:set SECRET_KEY=your-secret-key
    # heroku config:set DATABASE_URL=your-database-url
    # heroku config:set TOGETHER_API_KEY=your-together-api-key
    
    # Deploy
    # git push heroku main
    
    print_status "Heroku deployment completed!"
}

# Deploy to Railway (example)
deploy_railway() {
    print_status "Deploying to Railway..."
    
    # Check if Railway CLI is installed
    if ! command -v railway &> /dev/null; then
        print_error "Railway CLI is not installed. Please install it first."
        exit 1
    fi
    
    # Login to Railway
    # railway login
    
    # Deploy
    # railway up
    
    print_status "Railway deployment completed!"
}

# Main script
main() {
    print_status "Starting deployment process..."
    
    # Check prerequisites
    check_docker
    
    # Parse command line arguments
    if [ $# -eq 0 ]; then
        deploy_docker
    else
        deploy_platform $1
    fi
}

# Run main function with all arguments
main "$@" 