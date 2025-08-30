#!/bin/bash

echo "🐳 Starting AdvisorConnect GenAI v2 with Docker..."

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    echo "   Download from: https://www.docker.com/products/docker-desktop"
    exit 1
fi

# Check if Docker Compose is available
if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
    echo "❌ Docker Compose is not available. Please install Docker Compose first."
    echo "   It usually comes with Docker Desktop, or install separately."
    exit 1
fi

# Set compose command
if command -v docker-compose &> /dev/null; then
    COMPOSE_CMD="docker-compose"
else
    COMPOSE_CMD="docker compose"
fi

# Check if we're in the right directory
if [ ! -f "docker-compose.yml" ]; then
    echo "❌ Please run this script from the project root directory"
    exit 1
fi

# Check if OpenAI API key is set (optional)
if [ -z "$OPENAI_API_KEY" ]; then
    echo "⚠️  Note: OPENAI_API_KEY environment variable is not set."
    echo "   The system will work with fallback AI responses."
    echo "   To enable full AI functionality, set your OpenAI API key:"
    echo "   export OPENAI_API_KEY='your-api-key-here'"
    echo ""
fi

# Stop any existing containers
echo "🛑 Stopping any existing containers..."
$COMPOSE_CMD down

# Build and start the services
echo "🔨 Building and starting services..."
$COMPOSE_CMD up --build -d

# Wait for services to be ready
echo "⏳ Waiting for services to be ready..."
sleep 10

# Check service health
echo "🔍 Checking service health..."
$COMPOSE_CMD ps

echo ""
echo "✅ AdvisorConnect GenAI v2 is starting up!"
echo ""
echo "📊 Backend API: http://localhost:8000"
echo "📊 API Documentation: http://localhost:8000/docs"
echo "🎨 Frontend: http://localhost:3000"
echo ""
echo "🔍 Key Features Available:"
echo "   • ML Model Performance Dashboard: http://localhost:3000/admin/model-performance"
echo "   • Excel Upload & Training: Use the 'Upload Excel' button in Admin Cases"
echo "   • AI Advisor Recommendations: Submit new cases to see ML matching"
echo ""
echo "🐳 Docker Commands:"
echo "   • View logs: $COMPOSE_CMD logs -f"
echo "   • Stop services: $COMPOSE_CMD down"
echo "   • Restart services: $COMPOSE_CMD restart"
echo "   • Rebuild: $COMPOSE_CMD up --build"
echo ""
echo "Press Ctrl+C to stop (or run '$COMPOSE_CMD down')"
