# Makefile for Load Testing Suite

.PHONY: help build start stop test dashboard logs clean setup

# Default target
help:
	@echo "Load Testing Suite Commands"
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
	@echo "Testing:"
	@echo "  make test              - Run minimal load test"
	@echo "  make test-health       - Run only health checks"
	@echo "  make test-capabilities - Run only capabilities test"
	@echo "  make test-a2a          - Run only A2A communication test"
	@echo ""
	@echo "Monitoring:"
	@echo "  make dashboard - Open dashboard in browser"
	@echo "  make logs      - Show all logs"
	@echo "  make status    - Show service status"
	@echo ""
	@echo "Maintenance:"
	@echo "  make clean     - Clean up containers and volumes"
	@echo "  make reset     - Complete system reset"

# Setup and configuration
setup:
	@echo "Setting up Load Testing Suite..."
	@if [ ! -f .env ]; then \
		echo "Creating .env file from template..."; \
		cp .env.example .env; \
		echo ""; \
		echo "IMPORTANT: Please edit .env file and update Cloud Run URLs:"; \
		echo "  CREWAI_URL=https://crewai-agent-YOUR-PROJECT-ID.a.run.app/health"; \
		echo "  LANGRAPH_URL=https://langraph-agent-YOUR-PROJECT-ID.a.run.app/health"; \
		echo "  ADK_URL=https://adk-agent-YOUR-PROJECT-ID.a.run.app/health"; \
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
	@echo "Starting load testing stack..."
	@docker-compose up -d
	@echo "Services starting..."
	@sleep 5
	@echo ""
	@echo "Load Testing Suite is running:"
	@echo "  Load Tester API: http://localhost:8080"
	@echo "  Dashboard:       http://localhost:8081"
	@echo "  Redis:           localhost:6379"

# Stop all services
stop:
	@echo "Stopping load testing stack..."
	@docker-compose down

# Restart services
restart: stop start

# Run minimal load test
test:
	@echo "Running minimal load test..."
	@curl -X POST http://localhost:8080/test/start \
		-H "Content-Type: application/json" \
		-d '{"test_name": "minimal_test", "run_task_test": false}' \
		|| echo "Make sure services are running: make start"

# Run health check only
test-health:
	@echo "Running health check test..."
	@curl -X POST http://localhost:8080/test/start \
		-H "Content-Type: application/json" \
		-d '{"test_name": "health_check_only", "run_health_check": true, "run_capabilities": false, "run_a2a_test": false, "run_latency_test": false, "run_task_test": false}'

# Run capabilities test only
test-capabilities:
	@echo "Running capabilities test..."
	@curl -X POST http://localhost:8080/test/start \
		-H "Content-Type: application/json" \
		-d '{"test_name": "capabilities_only", "run_health_check": false, "run_capabilities": true, "run_a2a_test": false, "run_latency_test": false, "run_task_test": false}'

# Run A2A communication test only
test-a2a:
	@echo "Running A2A communication test..."
	@curl -X POST http://localhost:8080/test/start \
		-H "Content-Type: application/json" \
		-d '{"test_name": "a2a_only", "run_health_check": false, "run_capabilities": false, "run_a2a_test": true, "run_latency_test": false, "run_task_test": false}'

# Check test status
status:
	@echo "Load Testing Suite Status:"
	@docker-compose ps
	@echo ""
	@echo "Test Status:"
	@curl -s http://localhost:8080/test/status | python3 -m json.tool || echo "API not available"

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
quick-test:
	@echo "Running quick test..."
	@make test-health
	@sleep 3
	@echo "Test status:"
	@curl -s http://localhost:8080/test/status | python3 -m json.tool

# Show configuration
config:
	@echo "Current configuration:"
	@curl -s http://localhost:8080/config | python3 -m json.tool || echo "API not available"

# Install dependencies for local development
install-deps:
	@echo "Installing Python dependencies..."
	@pip install httpx asyncio redis fastapi uvicorn pydantic python-multipart
	@pip install jinja2 plotly pandas

# Run locally (without Docker)
run-local:
	@echo "Starting services locally..."
	@echo "Make sure Redis is running on localhost:6379"
	@python load_test_runner.py &
	@python dashboard/dashboard_app.py