#!/bin/bash

echo "=================================="
echo "📈 Investment Analyzer Setup"
echo "=================================="

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed"
    exit 1
fi

echo "✓ Python 3 found"

# Create virtual environment
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
    echo "✓ Virtual environment created"
else
    echo "✓ Virtual environment already exists"
fi

# Activate virtual environment
source venv/bin/activate
echo "✓ Virtual environment activated"

# Install dependencies
echo "📥 Installing dependencies..."
pip install -q -r requirements.txt
pip install -q streamlit pytest
echo "✓ Dependencies installed"

# Create data directory
mkdir -p data
echo "✓ Data directory ready"

# Run tests
echo ""
echo "🧪 Running tests..."
python3 -m pytest tests/ -v --tb=short | tail -20

echo ""
echo "=================================="
echo "✅ Setup Complete!"
echo "=================================="
echo ""
echo "Next steps:"
echo "1. Run the dashboard:"
echo "   streamlit run app.py"
echo ""
echo "2. Or run the demo:"
echo "   python3 demo.py"
echo ""
echo "Dashboard opens at: http://localhost:8501"
echo ""
