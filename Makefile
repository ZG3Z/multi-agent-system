# Multi-Agent System Makefile

.PHONY: help start stop test logs clean build status

# Default target
help:
	@echo "Multi-Agent System Commands"
	@echo ""
	@echo "Setup:"
	@echo "  make setup    - Initial setup and configuration"
	@echo "  make build    - Build all agent images"
	@echo ""
	@echo "Control:"
	@echo "  make start    - Start all agents"
	@echo "  make stop     - Stop all agents"
	@echo "  make restart  - Restart all agents"
	@echo ""
	@echo "Testing:"
	@echo "  make test           - Run tests (agents must be running)"
	@echo "  make test-with-startup - Start agents and run tests"
	@echo "  make health         - Check agent health"
	@echo ""
	@echo "Monitoring:"
	@echo "  make status   - Show system status"
	@echo "  make logs     - Show all logs"
	@echo "  make logs-f   - Follow all logs"
	@echo ""
	@echo "Maintenance:"
	@echo "  make clean    - Clean up containers and images"
	@echo "  make reset    - Complete system reset"

# Setup and configuration
setup:
	@echo "Setting up Multi-Agent System..."
	@chmod +x scripts/*.sh
	@./scripts/start-agents.sh

# Build all images
build:
	@echo "Building all agent images..."
	@docker-compose build

# Start the system
start:
	@echo "Starting agents..."
	@./scripts/start-agents.sh

# Stop the system  
stop:
	@echo "Stopping agents..."
	@./scripts/stop-agents.sh

# Restart the system
restart: stop start

# Check if agents are running and start if needed
test-with-startup:
	@echo "Ensuring agents are running..."
	@make start
	@echo "Running tests..."
	@./scripts/test-agents.sh

# Run tests (assumes agents are already running)
test:
	@echo "Running tests..."
	@./scripts/test-agents.sh

# Health check
health:
	@echo "Checking agent health..."
	@curl -s http://localhost:8080/health | jq '.status' 2>/dev/null || echo "Gemini Agent: Not responding"
	@curl -s http://localhost:8082/health | jq '.status' 2>/dev/null || echo "LangGraph Agent: Not responding"  
	@curl -s http://localhost:8083/health | jq '.status' 2>/dev/null || echo "ADK Agent: Not responding"

# Show system status
status:
	@echo "System Status:"
	@docker-compose ps

# View logs
logs:
	@./scripts/logs.sh

# Follow logs
logs-f:
	@./scripts/logs.sh -f

# Clean up
clean:
	@echo "Cleaning up..."
	@docker-compose down --rmi local -v

# Complete reset
reset:
	@echo "Resetting system..."
	@docker-compose down -v --rmi all
	@docker system prune -f
	@echo "System reset complete. Run 'make setup' to start fresh."

# Development helpers
dev-gemini:
	@docker-compose logs -f gemini-agent

dev-langraph:
	@docker-compose logs -f langraph-agent

dev-adk:
	@docker-compose logs -f adk-agent