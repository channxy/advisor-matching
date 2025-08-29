#!/bin/bash

echo "🚀 Starting AdvisorConnect GenAI v2..."

# Check if Python and Node.js are installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8+"
    exit 1
fi

if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed. Please install Node.js 16+"
    exit 1
fi

# Check if OpenAI API key is set
if [ -z "$OPENAI_API_KEY" ]; then
    echo "⚠️  Warning: OPENAI_API_KEY environment variable is not set."
    echo "   The AI features will use fallback responses."
    echo "   To enable full AI functionality, set your OpenAI API key:"
    echo "   export OPENAI_API_KEY='your-api-key-here'"
    echo ""
fi

# Start backend
echo "🔧 Starting backend server..."
cd backend

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "📦 Creating Python virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies
echo "📦 Installing Python dependencies..."
pip install -r requirements.txt

# Create sample Excel file
echo "📊 Creating sample Excel file..."
python create_sample_excel.py

# Start backend server in background
echo "🚀 Starting FastAPI backend on http://localhost:8000"
uvicorn main:app --reload --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!

# Wait a moment for backend to start
sleep 3

# Start frontend
echo "🎨 Starting frontend server..."
cd ../frontend

# Install dependencies if node_modules doesn't exist
if [ ! -d "node_modules" ]; then
    echo "📦 Installing Node.js dependencies..."
    npm install
fi

# Start frontend server
echo "🚀 Starting React frontend on http://localhost:3000"
npm start &
FRONTEND_PID=$!

echo ""
echo "✅ AdvisorConnect GenAI v2 is starting up!"
echo ""
echo "📊 Backend API: http://localhost:8000"
echo "📊 API Documentation: http://localhost:8000/docs"
echo "🎨 Frontend: http://localhost:3000"
echo ""
echo "Press Ctrl+C to stop both servers"

# Function to cleanup on exit
cleanup() {
    echo ""
    echo "🛑 Stopping servers..."
    kill $BACKEND_PID 2>/dev/null
    kill $FRONTEND_PID 2>/dev/null
    echo "✅ Servers stopped"
    exit 0
}

# Set up signal handlers
trap cleanup SIGINT SIGTERM

# Wait for both processes
wait
