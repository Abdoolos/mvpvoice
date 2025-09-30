#!/bin/bash
# AI Callcenter Agent Startup Script
# Designer: Abdullah Alawiss

set -e

echo "🚀 AI Callcenter Agent - Starting up..."
echo "Designer: Abdullah Alawiss"
echo "========================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker is not installed. Please install Docker first.${NC}"
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo -e "${RED}❌ Docker Compose is not installed. Please install Docker Compose first.${NC}"
    exit 1
fi

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo -e "${YELLOW}⚠️  Creating .env file from .env.example${NC}"
    cp .env.example .env
    echo -e "${BLUE}📝 Please edit .env file with your actual values${NC}"
fi

# Create necessary directories
echo -e "${BLUE}📁 Creating necessary directories...${NC}"
mkdir -p backend/uploads
mkdir -p data/sample_calls
mkdir -p ops/nginx/conf.d

# Build and start services
echo -e "${BLUE}🔧 Building Docker images...${NC}"
docker-compose build

echo -e "${BLUE}🐳 Starting services...${NC}"
docker-compose up -d

# Wait for services to be ready
echo -e "${YELLOW}⏳ Waiting for services to be ready...${NC}"
sleep 30

# Check service health
echo -e "${BLUE}🔍 Checking service health...${NC}"

# Check PostgreSQL
if docker-compose exec -T postgres pg_isready -U postgres > /dev/null 2>&1; then
    echo -e "${GREEN}✅ PostgreSQL is ready${NC}"
else
    echo -e "${RED}❌ PostgreSQL is not ready${NC}"
fi

# Check Redis
if docker-compose exec -T redis redis-cli ping > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Redis is ready${NC}"
else
    echo -e "${RED}❌ Redis is not ready${NC}"
fi

# Check Backend
if curl -f http://localhost:8000/health > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Backend API is ready${NC}"
else
    echo -e "${YELLOW}⚠️  Backend API is starting up...${NC}"
fi

# Check Frontend
if curl -f http://localhost:3000 > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Frontend is ready${NC}"
else
    echo -e "${YELLOW}⚠️  Frontend is starting up...${NC}"
fi

echo ""
echo -e "${GREEN}🎉 AI Callcenter Agent is starting up!${NC}"
echo ""
echo -e "${BLUE}📊 Available Services:${NC}"
echo -e "  Frontend Dashboard: ${GREEN}http://localhost:3000${NC}"
echo -e "  Backend API:        ${GREEN}http://localhost:8000${NC}"
echo -e "  API Documentation:  ${GREEN}http://localhost:8000/docs${NC}"
echo -e "  Celery Flower:      ${GREEN}http://localhost:5555${NC}"
echo -e "  PostgreSQL:         ${GREEN}localhost:5432${NC}"
echo -e "  Redis:              ${GREEN}localhost:6379${NC}"
echo ""
echo -e "${BLUE}🛠️  Useful Commands:${NC}"
echo -e "  View logs:          ${YELLOW}docker-compose logs -f${NC}"
echo -e "  Stop services:      ${YELLOW}docker-compose down${NC}"
echo -e "  Restart services:   ${YELLOW}docker-compose restart${NC}"
echo -e "  Run with Nginx:     ${YELLOW}docker-compose --profile production up -d${NC}"
echo ""
echo -e "${GREEN}🔧 Setup complete! Your AI Callcenter Agent is ready for Norwegian telecom compliance analysis.${NC}"
