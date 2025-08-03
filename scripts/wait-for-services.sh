#!/bin/bash

# Wait for services to be ready
echo "Waiting for services to be ready..."

services=(
    "localhost:8080:CrewAI"
    "localhost:8082:LangGraph" 
    "localhost:8083:ADK"
)

max_attempts=30
wait_time=5

for service_info in "${services[@]}"; do
    IFS=':' read -r host port name <<< "$service_info"
    
    echo "Waiting for $name service on $host:$port..."
    
    for i in $(seq 1 $max_attempts); do
        if curl -s -f "http://$host:$port/health" > /dev/null 2>&1; then
            echo "$name service is ready"
            break
        else
            if [ $i -eq $max_attempts ]; then
                echo "ERROR: $name service failed to start after $((max_attempts * wait_time)) seconds"
                exit 1
            else
                echo "Attempt $i/$max_attempts: $name service not ready, waiting ${wait_time}s..."
                sleep $wait_time
            fi
        fi
    done
done

echo "All services are ready!"