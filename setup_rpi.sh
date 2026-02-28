#!/bin/bash
# Raspberry Pi Setup Script for Wellbeing AI Companion
# Run this script after cloning the repository on your Raspberry Pi

set -e

echo "🚀 Setting up Wellbeing AI Companion on Raspberry Pi..."
echo ""

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install it first:"
    echo "   sudo apt update && sudo apt install python3 python3-pip python3-venv"
    exit 1
fi

echo "✓ Python 3 found"

# Create virtual environment
echo "📦 Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "⬆️  Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "📥 Installing Python dependencies..."
pip install -r requirements.txt

# Create data directory
echo "📁 Creating data directory..."
mkdir -p data/memory

# Check if Ollama is installed
echo ""
echo "🤖 Checking Ollama installation..."
if ! command -v ollama &> /dev/null; then
    echo "⚠️  Ollama is not installed."
    echo ""
    echo "To install Ollama on Raspberry Pi:"
    echo "   curl -fsSL https://ollama.com/install.sh | sh"
    echo ""
    read -p "Would you like to install Ollama now? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        curl -fsSL https://ollama.com/install.sh | sh
    fi
else
    echo "✓ Ollama is installed"
fi

# Check if Ollama is running
if pgrep -x "ollama" > /dev/null; then
    echo "✓ Ollama is running"
else
    echo "⚠️  Ollama is not running. Starting Ollama..."
    ollama serve &
    sleep 3
fi

# Pull the model
echo ""
echo "📥 Pulling phi3:mini model (this may take a while)..."
ollama pull phi3:mini

# Camera setup reminder
echo ""
echo "📷 Camera Setup:"
echo "   If you're using the Raspberry Pi Camera Module:"
echo "   1. Enable camera: sudo raspi-config → Interface Options → Camera"
echo "   2. Reboot if needed"
echo "   3. Set CAMERA_ENABLED=True in config/config.py"
echo ""

# Display completion message
echo "✅ Setup complete!"
echo ""
echo "To run the terminal version:"
echo "   source venv/bin/activate"
echo "   python main.py"
echo ""
echo "To run the web interface:"
echo "   source venv/bin/activate"
echo "   python web_app.py"
echo "   Then open: http://localhost:5000"
echo ""
echo "💙 Enjoy your Wellbeing AI Companion!"
