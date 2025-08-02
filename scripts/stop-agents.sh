#!/bin/bash

# Multi-Agent System Shutdown Script
echo "Stopping Multi-Agent System..."

# Stop all containers
docker-compose down

# Optional: Remove images (uncomment if you want to clean up)
# echo "Cleaning up images..."
# docker-compose down --rmi all

# Optional: Remove volumes (uncomment if you want to clean up data)
# echo "Cleaning up volumes..."
# docker-compose down -v

echo "Multi-Agent System stopped"
echo ""
echo "To remove all data: docker-compose down -v --rmi all"
echo "To restart: ./scripts/start-agents.sh"