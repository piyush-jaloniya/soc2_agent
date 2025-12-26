#!/bin/bash

# SOC 2 Compliance Platform - Run Script

# Set Python path to include project root
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}Starting SOC 2 Compliance Platform...${NC}"
echo ""
echo "🛡️  SOC 2 AI Compliance Agent"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo -e "${GREEN}✓${NC} Dashboard:      http://localhost:8000"
echo -e "${GREEN}✓${NC} API Docs:       http://localhost:8000/docs"
echo -e "${GREEN}✓${NC} Health Check:   http://localhost:8000/health"
echo ""
echo "Press CTRL+C to stop the server"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Run the application
python backend/api/main.py
