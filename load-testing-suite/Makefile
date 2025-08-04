# Makefile for 3-Level Load Testing Suite

.PHONY: help build start stop test dashboard logs clean setup

# Default target
help:
	@echo "3-Level Load Testing Suite Commands"
	@echo ""
	@echo "Setup:"
	@echo "  make setup     - Initial setup and configuration"
	@echo "  make build     - Build Docker images"
	@echo ""
	@echo "Control:"
	@echo "  make start     - Start load testing stack"
	@echo "  make stop      - Stop all services"
	@echo "  make restart   - Restart all services"
	@echo ""
	@echo "Testing Levels:"
	@echo "  make test-level1   - Run Level 1: Basic tests (9 requests)"
	@echo "  make test-level2   - Run Level 2: Functional tests (12-15 requests)"
	@echo "  make test-level3   - Run Level 3: Workflow tests (15-18 requests)"
	@echo "  make test-all      - Run all 3 levels sequentially"
	@echo ""
	@echo "Legacy Commands:"
	@echo "  make test          - Run Level 1 (default)"
	@echo "  make test-health   - Run basic health check"
	@echo ""
	@echo "Monitoring:"
	@echo "  make dashboard     - Open dashboard in browser"
	@echo "  make logs          - Show all logs"
	@echo "  make status        - Show service status"
	@echo ""
	@echo "Maintenance:"
	@echo "  make clean         - Clean up containers and volumes"
	@echo "  make reset         - Complete system reset"

# Setup and configuration
setup:
	@echo "Setting up 3-Level Load Testing Suite..."
	@if [ ! -f .env ]; then \
		echo "Creating .env file from template..."; \
		cp .env.example .env; \
		echo ""; \
		echo "IMPORTANT: Please edit .env file and update Cloud Run URLs:"; \
		echo "  CREWAI_URL=https://crewai-agent-YOUR-PROJECT-ID.a.run.app"; \
		echo "  LANGRAPH_URL=https://langraph-agent-YOUR-PROJECT-ID.a.run.app"; \
		echo "  ADK_URL=https://adk-agent-YOUR-PROJECT-ID.a.run.app"; \
		echo ""; \
	fi
	@mkdir -p results config dashboard/templates
	@echo "Setup complete!"

# Build Docker images
build:
	@echo "Building Docker images..."
	@docker-compose build

# Start the testing stack
start:
	@echo "Starting 3-level load testing stack..."
	@docker-compose up -d
	@echo "Services starting..."
	@sleep 5
	@echo ""
	@echo "3-Level Load Testing Suite is running:"
	@echo "  Load Tester API: http://localhost:8080"
	@echo "  Dashboard:       http://localhost:8081"
	@echo "  Redis:           localhost:6379"
	@echo ""
	@echo "Available test levels:"
	@echo "  Level 1: Basic tests (9 requests)"
	@echo "  Level 2: Functional tests (12-15 requests)"
	@echo "  Level 3: Workflow tests (15-18 requests)"

# Stop all services
stop:
	@echo "Stopping load testing stack..."
	@docker-compose down

# Restart services
restart: stop start

# Test Level 1: Basic Tests
test-level1:
	@echo "Running Level 1: Basic Tests (9 requests)..."
	@curl -X POST http://localhost:8080/test/start \
		-H "Content-Type: application/json" \
		-d '{"test_name": "level1_basic", "test_level": 1}' \
		|| echo "Make sure services are running: make start"

# Test Level 2: Functional Tests
test-level2:
	@echo "Running Level 2: Functional Tests (12-15 requests)..."
	@curl -X POST http://localhost:8080/test/start \
		-H "Content-Type: application/json" \
		-d '{"test_name": "level2_functional", "test_level": 2}' \
		|| echo "Make sure services are running: make start"

# Test Level 3: Workflow Tests
test-level3:
	@echo "Running Level 3: Workflow Tests (15-18 requests)..."
	@curl -X POST http://localhost:8080/test/start \
		-H "Content-Type: application/json" \
		-d '{"test_name": "level3_workflow", "test_level": 3}' \
		|| echo "Make sure services are running: make start"

# Run all levels sequentially
test-all:
	@echo "Running all 3 test levels sequentially..."
	@echo "Starting with Level 1..."
	@make test-level1
	@sleep 30
	@echo "Starting Level 2..."
	@make test-level2
	@sleep 45
	@echo "Starting Level 3..."
	@make test-level3
	@echo "All levels completed!"

# Legacy: Run Level 1 (backwards compatibility)
test: test-level1

# Legacy: Health check
test-health:
	@echo "Running basic health check..."
	@curl -X POST http://localhost:8080/test/start \
		-H "Content-Type: application/json" \
		-d '{"test_name": "health_check", "test_level": 1}' \
		|| echo "Make sure services are running: make start"

# Check test status
status:
	@echo "3-Level Load Testing Suite Status:"
	@docker-compose ps
	@echo ""
	@echo "Test Status:"
	@curl -s http://localhost:8080/test/status | python3 -m json.tool || echo "API not available"
	@echo ""
	@echo "Configuration:"
	@curl -s http://localhost:8080/config | python3 -m json.tool || echo "API not available"

# Open dashboard
dashboard:
	@echo "Opening dashboard..."
	@if command -v xdg-open > /dev/null; then \
		xdg-open http://localhost:8081; \
	elif command -v open > /dev/null; then \
		open http://localhost:8081; \
	else \
		echo "Dashboard available at: http://localhost:8081"; \
	fi

# View logs
logs:
	@echo "Showing logs..."
	@docker-compose logs --tail=50 -f

# View specific service logs
logs-tester:
	@docker-compose logs -f load-tester

logs-dashboard:
	@docker-compose logs -f dashboard

logs-redis:
	@docker-compose logs -f redis

# Clean up
clean:
	@echo "Cleaning up..."
	@docker-compose down -v
	@docker system prune -f

# Complete reset
reset: clean
	@echo "Resetting system..."
	@docker-compose down -v --rmi all
	@rm -rf results/*
	@echo "System reset complete. Run 'make setup' to start fresh."

# Development helpers
dev-build:
	@docker-compose build --no-cache

dev-logs:
	@docker-compose logs -f load-tester dashboard

# Quick test with status check
quick-test: test-level1
	@sleep 10
	@echo "Test status:"
	@curl -s http://localhost:8080/test/status | python3 -m json.tool

# Show configuration
config:
	@echo "Current configuration:"
	@curl -s http://localhost:8080/config | python3 -m json.tool || echo "API not available"

# Show available test results
results:
	@echo "Available test results:"
	@curl -s http://localhost:8080/test/results | python3 -m json.tool || echo "API not available"

# Install dependencies for local development
install-deps:
	@echo "Installing Python dependencies..."
	@pip install httpx asyncio redis fastapi uvicorn pydantic python-multipart

# Run locally (without Docker)
run-local:
	@echo "Starting services locally..."
	@echo "Make sure Redis is running on localhost:6379"
	@python load_test_runner.py