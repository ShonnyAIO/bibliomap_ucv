#!/bin/bash

# Navigate to the script's directory
cd "$(dirname "$0")"

# Check if .venv exists, if not create it
if [ ! -d ".venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv .venv
fi

# Activate the virtual environment
source .venv/bin/activate

# Install dependencies if requirements.txt exists and is updated
if [ -f "requirements.txt" ]; then
    echo "Checking/Installing dependencies..."
    pip install -r requirements.txt
fi

# Run the Streamlit application
echo "Starting BiblioMap UCV Streamlit app..."
streamlit run app/streamlit_app.py
