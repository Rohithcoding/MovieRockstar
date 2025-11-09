#!/bin/bash

# Install Python dependencies
pip install -r requirements.txt

# Set environment variables
export STREAMLIT_SERVER_HEADLESS=true
export ENABLE_CORS=true

# Make the script executable
chmod +x setup.sh
