# Multi-Agent System Makefile

.PHONY: help start stop test logs clean build status ci lint format

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
	@echo "  make ci             - Run full CI pipeline locally"
	@echo ""
	@echo "Code Quality:"
	@echo "  make lint     - Run linting checks"
	@echo "  make format   - Format code with black and isort"
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
	@python -m pytest tests/ -v

# Health check
health:
	@echo "Checking agent health..."
	@curl -s http://localhost:8080/health | jq '.status' 2>/dev/null || echo "CrewAI Agent: Not responding"    # ← ZMIEŃ
	@curl -s http://localhost:8082/health | jq '.status' 2>/dev/null || echo "LangGraph Agent: Not responding"  # ← ZMIEŃ
	@curl -s http://localhost:8083/health | jq '.status' 2>/dev/null || echo "ADK Agent: Not responding"        # ← ZMIEŃ

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

# Code quality targets
lint:
	@echo "Running linting checks..."
	@python -m flake8 agents/ --max-line-length=127 --extend-ignore=E203,W503
	@echo "Checking code formatting..."
	@python -m black --check agents/
	@echo "Checking import sorting..."
	@python -m isort --check-only agents/

format:
	@echo "Formatting code..."
	@python -m black agents/
	@python -m isort agents/
	@echo "Code formatted!"

# CI pipeline (run locally)
ci: lint build test-ci-env
	@echo "CI pipeline completed successfully!"

# Test with CI environment (fake API keys)
test-ci-env:
	@echo "Setting up CI test environment..."
	@for agent in crewai-agent langraph-agent adk-agent; do \
		echo "GOOGLE_API_KEY=test-key-for-ci" > agents/$$agent/.env; \
		echo "GEMINI_MODEL=gemini-2.0-flash-exp" >> agents/$$agent/.env; \
	done
	@make start
	@sleep 30
	@chmod +x scripts/wait-for-services.sh
	@./scripts/wait-for-services.sh
	@python -m pytest tests/test_ci_integration.py -v
	@make stop

# Development helpers
dev-crewai:
	@docker-compose logs -f crewai-agent

dev-langraph:
	@docker-compose logs -f langraph-agent

dev-adk:
	@docker-compose logs -f adk-agent

# Install development dependencies
install-dev:
	@echo "Installing development dependencies..."
	@pip install flake8 black isort pytest pytest-asyncio httpx

# Docker image testing
test-images:
	@echo "Testing Docker images..."
	@for agent in crewai-agent langraph-agent adk-agent; do \
		echo "Testing $$agent image..."; \
		docker build -t $$agent:test agents/$$agent/; \
		docker run --rm $$agent:test python -c "print('$$agent image OK')"; \
	done