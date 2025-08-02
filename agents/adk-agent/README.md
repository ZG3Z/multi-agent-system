# ADK Agent

ADK-powered data processing agent with standardized API interface, ready for A2A communication.

## Features

- ✅ Standard REST API (`/execute`, `/capabilities`, `/health`, `/spec`)
- ✅ Advanced data processing capabilities (transformation, analysis, validation, aggregation)
- ✅ Pandas & NumPy integration for robust data handling
- ✅ Statistical analysis with SciPy
- ✅ Google Gemini integration for insights
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
docker build -t adk-agent .

# Run agent (loads .env automatically)
docker run -p 8083:8083 --env-file .env adk-agent
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
Execute data processing tasks
```json
{
  "task_type": "data_transformation",
  "description": "Transform customer data to normalized format",
  "context": {
    "data": {"records": [...]},
    "target_format": "json",
    "transformations": ["normalize_columns"]
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
    "name": "data_transformation",
    "description": "Transform data between formats and structures",
    "estimated_duration": 60
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
  "agent_id": "adk-agent",
  "agent_type": "adk",
  "a2a_ready": false
}
```

## Supported Task Types

- **data_transformation**: Transform data between formats and structures
- **data_analysis**: Perform statistical analysis and generate insights
- **data_validation**: Validate data quality, integrity, and completeness
- **data_aggregation**: Aggregate and summarize datasets

## Data Processing Features

- **Pandas Integration**: Robust data manipulation and transformation
- **Statistical Analysis**: Descriptive statistics, hypothesis testing, distribution analysis
- **Data Validation**: Quality checks, missing value detection, format validation
- **Aggregation**: Groupby operations, summary statistics, multi-level aggregation
- **AI Insights**: Gemini-powered analysis and recommendations

## Sample Data Processing

The agent can work with:
- JSON records
- CSV-like data structures
- Statistical datasets
- Time series data
- Categorical data

## Next Steps

1. Test this agent locally
2. Implement A2A communication protocol
3. Enable collaboration between all 3 agents
4. Deploy to Cloud Run