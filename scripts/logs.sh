#!/bin/bash

# Multi-Agent System Logs Viewer
echo "Multi-Agent System Logs"

# Check if agents are running
if ! docker-compose ps | grep -q "Up"; then
    echo "Agents are not running. Start them first:"
    echo "./scripts/start-agents.sh"
    exit 1
fi

# Parse command line arguments
AGENT=""
FOLLOW=""

while [[ $# -gt 0 ]]; do
    case $1 in
        -f|--follow)
            FOLLOW="-f"
            shift
            ;;
        gemini|langraph|adk)
            AGENT="$1-agent"
            shift
            ;;
        *)
            echo "Usage: $0 [gemini|langraph|adk] [-f|--follow]"
            echo ""
            echo "Examples:"
            echo "$0                    # Show logs for all agents"
            echo "$0 gemini             # Show logs for gemini agent only"
            echo "$0 langraph -f        # Follow logs for langraph agent"
            echo "$0 -f                 # Follow logs for all agents"
            exit 1
            ;;
    esac
done

# Show logs
if [ -n "$AGENT" ]; then
    echo "Showing logs for $AGENT..."
    docker-compose logs $FOLLOW $AGENT
else
    echo "Showing logs for all agents..."
    docker-compose logs $FOLLOW
fi