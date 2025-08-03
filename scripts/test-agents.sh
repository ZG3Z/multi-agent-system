#!/bin/bash

# Multi-Agent System Testing Script
echo "Testing Multi-Agent System..."

# Check if agents are running
echo "Checking if agents are running..."
if ! docker-compose ps | grep -q "Up"; then
    echo "Agents are not running. Start them first:"
    echo "./scripts/start-agents.sh"
    exit 1
fi

# Basic health checks
echo "Basic health checks..."
agents=("8080:CrewAI" "8082:LangGraph" "8083:ADK")

for agent_info in "${agents[@]}"; do
    port=$(echo $agent_info | cut -d: -f1)
    name=$(echo $agent_info | cut -d: -f2)
    
    if curl -s -f "http://localhost:$port/health" > /dev/null; then
        echo "$name Agent (port $port) is healthy"
    else
        echo "$name Agent (port $port) is not responding"
    fi
done

echo ""

# Run A2A communication tests
echo "Running A2A communication tests..."
if [ -f "tests/test_a2a_communication.py" ]; then
    python tests/test_a2a_communication.py
else
    echo "tests/test_a2a_communication.py not found"
fi

echo ""
echo "Running individual agent tests..."

# Test individual agents
agents=("crewai" "langraph" "adk")
for agent in "${agents[@]}"; do
    if [ -f "tests/test_${agent}_agent.py" ]; then
        echo "Testing $agent agent..."
        python tests/test_${agent}_agent.py
        echo ""
    fi
done

echo ""
echo "View detailed logs:"
echo "docker-compose logs crewai-agent"
echo "docker-compose logs langraph-agent" 
echo "docker-compose logs adk-agent"
echo ""
echo "Manual testing:"
echo "curl http://localhost:8080/spec"
echo "curl http://localhost:8082/capabilities"
echo "curl http://localhost:8083/health"