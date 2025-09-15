#!/bin/bash
# FastAPI Backend Startup Script
# AI-based Drop-out Prediction and Counseling System

echo "Starting AI-based Drop-out Prediction System Backend..."
echo "=========================================="

# Set environment variables (modify as needed)
export MONGO_URI="${MONGO_URI:-mongodb://localhost:27017}"
export DB_NAME="${DB_NAME:-dropout_prediction}"

# Display configuration
echo "Configuration:"
echo "  MongoDB URI: $MONGO_URI"
echo "  Database Name: $DB_NAME"
echo "  Server Host: 0.0.0.0"
echo "  Server Port: 8000"
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Virtual environment not found. Creating one..."
    python -m venv venv
fi

# Activate virtual environment (Linux/Mac)
if [ -f "venv/bin/activate" ]; then
    echo "Activating virtual environment..."
    source venv/bin/activate
elif [ -f "venv/Scripts/activate" ]; then
    # Windows
    echo "Activating virtual environment (Windows)..."
    source venv/Scripts/activate
fi

# Install requirements
echo "Installing requirements..."
pip install -r requirements.txt

# Change to app directory
cd app

# Start the server
echo "Starting FastAPI server..."
echo "API Documentation will be available at:"
echo "  - Swagger UI: http://localhost:8000/docs"
echo "  - ReDoc: http://localhost:8000/redoc"
echo ""

uvicorn main:app --host 0.0.0.0 --port 8000 --reload
