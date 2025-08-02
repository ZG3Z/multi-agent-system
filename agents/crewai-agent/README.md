# Gemini AI Agent

Gemini-powered agent with standardized API interface, ready for A2A communication.

## Features

- ✅ Standard REST API (`/execute`, `/capabilities`, `/health`, `/spec`)
- ✅ Google Gemini integration for research, analysis, planning, and writing tasks
- ✅ Direct Gemini API integration (no CrewAI dependencies)
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
GEMINI_MODEL=gemini/gemini-2.5-flash
```

### 2. Run with Docker
```bash
# Build image
docker build -t crewai-agent .

# Run agent (loads .env automatically)
docker run -p 8081:8080 --env-file .env crewai-agent
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
Execute tasks with CrewAI
```json
{
  "task_type": "research",
  "description": "Research AI trends in 2024",
  "context": {"focus": "enterprise AI"},
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
    "name": "research",
    "description": "Research topics and gather information",
    "estimated_duration": 180
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
  "agent_id": "crewai-agent",
  "agent_type": "crewai",
  "a2a_ready": false
}
```

## Supported Task Types

- **research**: Research topics and gather information
- **analysis**: Analyze data and provide insights  
- **planning**: Create strategic plans and roadmaps
- **writing**: Generate high-quality written content

## Next Steps

1. Test this agent locally
2. Implement LangGraph agent with same interface
3. Add A2A communication between agents
4. Deploy to Cloud Run