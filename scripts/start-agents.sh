#!/bin/bash

# Multi-Agent System Startup Script
echo "Starting Multi-Agent System..."

# Check if .env files exist
echo "Checking environment files..."
for agent in agents/crewai-agent agents/langraph-agent agents/adk-agent; do
    if [ ! -f "./$agent/.env" ]; then
        echo "Missing .env file for $agent"
        echo "Copying from .env.example..."
        cp "./$agent/.env.example" "./$agent/.env"
        echo "Please edit ./$agent/.env and add your GOOGLE_API_KEY"
    fi
done

# Check if GOOGLE_API_KEY is set
echo "Checking API keys..."
if ! grep -q "GOOGLE_API_KEY=.*[^=]" ./agents/crewai-agent/.env 2>/dev/null; then
    echo "GOOGLE_API_KEY not found in agents/crewai-agent/.env"
    echo "Please add your Google API key to all .env files"
    exit 1
fi

# Build and start all agents
echo "Building and starting agents..."
docker-compose up --build -d

# Wait for agents to be ready
echo "Waiting for agents to start..."
sleep 10

# Check agent health
echo "Checking agent health..."
agents=("gemini-agent:8080" "langraph-agent:8082" "adk-agent:8083")

for agent_info in "${agents[@]}"; do
    agent_name=$(echo $agent_info | cut -d: -f1)
    port=$(echo $agent_info | cut -d: -f2)
    
    echo "Checking $agent_name on port $port..."
    
    # Wait up to 60 seconds for agent to be ready
    for i in {1..12}; do
        if curl -s -f "http://localhost:$port/health" > /dev/null 2>&1; then
            echo "$agent_name is healthy"
            break
        else
            if [ $i -eq 12 ]; then
                echo "$agent_name failed to start"
                echo "Check logs: docker logs $agent_name"
            else
                echo "Waiting for $agent_name... ($i/12)"
                sleep 5
            fi
        fi
    done
done

echo ""
echo "Multi-Agent System Status:"
echo "CrewAI Agent:    http://localhost:8080"  # ← ZMIEŃ
echo "LangGraph Agent: http://localhost:8082"  # ← ZMIEŃ  
echo "ADK Agent:       http://localhost:8083"  # ← ZMIEŃ
echo ""
echo "View logs: docker-compose logs -f [agent-name]"
echo "Stop system: ./scripts/stop-agents.sh"
echo "Run tests: python test_a2a_communication.py"