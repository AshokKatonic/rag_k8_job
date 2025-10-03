#!/bin/bash

# Activation script for the virtual environment
# Usage: source activate.sh

echo "Activating virtual environment..."

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Virtual environment not found. Creating one..."
    python3 -m venv venv
    echo "Installing dependencies..."
    source venv/bin/activate && pip install --upgrade pip && pip install -r requirements.txt
fi

# Activate the virtual environment
source venv/bin/activate

echo "Virtual environment activated!"
echo "You can now run: python main.py"
echo "To deactivate, run: deactivate"
