#!/bin/bash
# Quick Start Guide for Carbon Brokers Backend

echo "================================"
echo "Carbon Brokers Backend - Quick Start"
echo "================================"
echo ""

# Activate virtual environment
echo "[1/4] Activating Python virtual environment..."
source ../venv/bin/activate  # For Linux/Mac
# For Windows: ..\.venv\Scripts\Activate.ps1

# Install dependencies (if needed)
echo "[2/4] Installing Python dependencies..."
pip install -r requirements.txt

# Initialize database
echo "[3/4] Initializing database..."
python -c "from app.database import engine, Base; from app import models; Base.metadata.create_all(bind=engine); print('Database ready!')"

# Start the FastAPI server
echo "[4/4] Starting FastAPI server..."
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

echo ""
echo "================================"
echo "Backend is running!"
echo "API URL: http://localhost:8000"
echo "API Docs: http://localhost:8000/docs"
echo "================================"
