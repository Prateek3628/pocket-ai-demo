#!/bin/bash

# Deployment script for AWS EC2
# This script sets up and runs the Streamlit application

set -e  # Exit on error

echo "Starting deployment setup..."

# Update system packages
echo "Updating system packages..."
sudo apt-get update
sudo apt-get upgrade -y

# Install Python and pip if not already installed
echo "Installing Python and pip..."
sudo apt-get install -y python3 python3-pip python3-venv

# Install nginx for reverse proxy
echo "Installing nginx..."
sudo apt-get install -y nginx

# Create application directory if it doesn't exist
APP_DIR="/home/ubuntu/pocket-ai-demo"
if [ ! -d "$APP_DIR" ]; then
    mkdir -p "$APP_DIR"
fi

cd "$APP_DIR"

# Create virtual environment
echo "Creating virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Install dependencies
echo "Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "Creating .env file..."
    echo "OPENAI_API_KEY=your_openai_api_key_here" > .env
    echo "⚠️  IMPORTANT: Edit .env file and add your actual OpenAI API key!"
fi

echo "✅ Deployment setup complete!"
echo ""
echo "Next steps:"
echo "1. Edit .env file with your OpenAI API key"
echo "2. Run: sudo systemctl start streamlit"
echo "3. Access your app at http://your-ec2-public-ip:8501"
