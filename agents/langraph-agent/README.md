# LangGraph Agent

LangGraph-powered agent with standardized API interface, ready for A2A communication.

## Features

- ✅ Standard REST API (`/execute`, `/capabilities`, `/health`, `/spec`)
- ✅ LangGraph integration for decision-making, workflows, routing, and conditional logic
- ✅ Google Gemini integration
- ✅ State management with workflows
- ✅ Docker containerization
- ✅ Async task execution
- ⏳ A2A communication (coming next)

## Quick Start

### 1. Environment Setup
```bash
# Get Google API key from AI Studio
# Go to: https://aistudio.google.com/app/apikey
# Create new API key

# Copy example env file
cp .env.example .env

# Edit .env file and add your Google API key
GOOGLE_API_KEY=your-google-api-key-here
GEMINI_MODEL=gemini-2.0-flash-exp
```

### 2. Run with Docker
```bash
# Build image
docker build -t langraph-agent .

# Run agent (loads .env automatically)
docker run -p 8082:8082 --env-file .env langraph-agent
```

### 3. Run locally (development)
```bash
# Install dependencies
pip install -r requirements.txt

# Create .env file (see step 1)
# Environment is loaded automatically

# Run agent
python main.py
```

## Testing

```bash
# Run test client
python test_client.py
```

## API Endpoints

### POST `/execute`
Execute tasks with LangGraph
```json
{
  "task_type": "decision_making",
  "description": "Choose the best option",
  "context": {
    "options": ["A", "B", "C"],
    "criteria": {"cost": "important"}
  },
  "collaborators": {
    "analyzer": "http://other-agent.com"
  }
}
```

### GET `/capabilities`
Get agent capabilities
```json
[
  {
    "name": "decision_making",
    "description": "Make decisions based on input criteria",
    "estimated_duration": 120
  }
]
```

### GET `/health`
Health check
```json
{
  "status": "healthy",
  "uptime": 3600,
  "active_tasks": 0
}
```

### GET `/spec`
Agent specification
```json
{
  "agent_id": "langraph-agent",
  "agent_type": "langraph",
  "a2a_ready": false
}
```

## Supported Task Types

- **decision_making**: Make decisions based on criteria and options
- **workflow**: Execute multi-step workflows with state management
- **routing**: Route requests to appropriate handlers based on rules
- **conditional_logic**: Execute conditional logic and branching

## LangGraph Features

- **State Management**: Maintain state across workflow steps
- **Conditional Routing**: Branch based on conditions
- **Multi-step Workflows**: Execute complex sequences
- **Memory Checkpointing**: Save and restore workflow state

## Next Steps

1. Test this agent locally
2. Implement ADK agent with same interface
3. Add A2A communication between agents
4. Deploy to Cloud Run