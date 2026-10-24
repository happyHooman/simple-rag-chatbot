#!/bin/bash

# Test script for Docker setup

set -e

echo "🧪 Testing Docker setup..."

# Test 1: Check if containers are running
echo "📋 Checking container status..."
docker-compose ps

# Test 2: Check app health
echo "🏥 Testing app health..."
if curl -f http://localhost:8000/health > /dev/null 2>&1; then
    echo "✅ App health check passed"
else
    echo "❌ App health check failed"
    exit 1
fi

# Test 3: Check database connection
echo "🗄️  Testing database connection..."
if docker-compose exec -T postgres pg_isready -U postgres > /dev/null 2>&1; then
    echo "✅ Database connection successful"
else
    echo "❌ Database connection failed"
    exit 1
fi

# Test 4: Test API endpoint
echo "🔍 Testing API endpoint..."
response=$(curl -s -X POST http://localhost:8000/ask-question \
    -H "Content-Type: application/json" \
    -d '{"user_question": "How do I reset my password?"}')

if echo "$response" | grep -q "source"; then
    echo "✅ API endpoint working"
    echo "📄 Response: $response"
else
    echo "❌ API endpoint failed"
    echo "📄 Response: $response"
    exit 1
fi

echo "🎉 All tests passed! Docker setup is working correctly."
