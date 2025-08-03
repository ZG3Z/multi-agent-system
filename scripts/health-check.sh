#!/bin/bash

# Health check script for CI
echo "Running health checks..."

services=(
    "8080:CrewAI"
    "8082:LangGraph"
    "8083:ADK"
)

all_healthy=true

for service_info in "${services[@]}"; do
    IFS=':' read -r port name <<< "$service_info"
    
    echo "Checking $name service on port $port..."
    
    if response=$(curl -s "http://localhost:$port/health"); then
        status=$(echo "$response" | python3 -c "import sys, json; print(json.load(sys.stdin).get('status', 'unknown'))")
        if [ "$status" = "healthy" ]; then
            echo "✓ $name service is healthy"
        else
            echo "✗ $name service status: $status"
            all_healthy=false
        fi
    else
        echo "✗ $name service is not responding"
        all_healthy=false
    fi
done

if [ "$all_healthy" = true ]; then
    echo "All services are healthy!"
    exit 0
else
    echo "Some services are not healthy"
    exit 1
fi