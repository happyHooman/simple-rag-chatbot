#!/bin/bash

# Docker setup script for FAQ Assistant

set -e

echo "🐳 Setting up FAQ Assistant with Docker..."

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker and try again."
    exit 1
fi

# Check if .env file exists
if [ ! -f .env ]; then
    echo "⚠️  .env file not found. Creating from template..."
    cat > .env << EOF
# OpenAI API Key (required)
OPENAI_API_KEY=your_openai_api_key_here

# Database Configuration
DATABASE_URL=postgresql://postgres:postgres@postgres:5432/faq_embeddings

# API Configuration
API_TITLE=Q&A Service
API_VERSION=1.0.0
API_DESCRIPTION=FastAPI-based Q&A service with LangChain integration

# Server Configuration
HOST=0.0.0.0
PORT=8000
DEBUG=false
LOG_LEVEL=INFO

# Q&A Service Settings
SIMILARITY_THRESHOLD=0.5

# OpenAI Chat Model Settings
OPENAI_CHAT_MODEL=gpt-4o-mini
OPENAI_CHAT_TEMPERATURE=0.7
EOF
    echo "📝 Please edit .env file and add your OpenAI API key"
    echo "   Then run this script again."
    exit 1
fi

# Build and start services
echo "🔨 Building and starting services..."
docker-compose up --build -d

# Wait for services to be healthy
echo "⏳ Waiting for services to be ready..."
sleep 10

# Check if services are running
if docker-compose ps | grep -q "Up"; then
    echo "✅ Services are running!"
    echo ""
    echo "🌐 Application: http://localhost:8000"
    echo "📚 API Docs: http://localhost:8000/docs"
    echo "🗄️  Database: localhost:5432"
    echo ""
    echo "📋 Useful commands:"
    echo "   docker-compose logs -f app     # View app logs"
    echo "   docker-compose logs -f postgres # View database logs"
    echo "   docker-compose down            # Stop services"
    echo "   docker-compose restart app     # Restart app only"
else
    echo "❌ Services failed to start. Check logs with:"
    echo "   docker-compose logs"
    exit 1
fi
