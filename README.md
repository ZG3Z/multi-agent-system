# Multi-Agent System with A2A Communication

Enterprise-grade multi-agent system with Agent-to-Agent (A2A) communication protocol. Three specialized AI agents working together through standardized interfaces.

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   CrewAI Agent  │◄──►│  LangGraph      │◄──►│   ADK Agent     │
│   (Research)    │    │  Agent          │    │   (Data Proc.)  │
│   Port: 8080    │    │  (Decisions)    │    │   Port: 8083    │
│                 │    │  Port: 8082     │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
                    ┌─────────────────┐
                    │   A2A Protocol  │
                    │  (Universal)    │
                    └─────────────────┘
```

## 🚀 Quick Start

### Prerequisites
- Docker & Docker Compose
- Google API Key from [AI Studio](https://aistudio.google.com/app/apikey)

### 1. Setup Environment
```bash
# Clone or download the project
git clone <repository-url>
cd multi-agent-system

# Make scripts executable
chmod +x scripts/*.sh

# Start the system (will guide you through setup)
./scripts/start-agents.sh
```

### 2. Configure API Keys
The startup script will create `.env` files for each agent. Add your Google API key:

```bash
# Edit each agent's .env file
nano agents/crewai-agent/.env
nano agents/langraph-agent/.env  
nano agents/adk-agent/.env

# Add your API key:
GOOGLE_API_KEY=your-google-api-key-here
```

### 3. Start Agents
```bash
./scripts/start-agents.sh
```

### 4. Test the System
```bash
./scripts/test-agents.sh
```

## 🎯 Agent Capabilities

### CrewAI Agent (Port 8080)
- **Research**: Comprehensive topic research and information gathering
- **Analysis**: Data analysis and insight generation
- **Planning**: Strategic planning and roadmap creation
- **Writing**: High-quality content generation

### LangGraph Agent (Port 8082)  
- **Decision Making**: Multi-criteria decision analysis
- **Workflows**: Complex multi-step process execution
- **Routing**: Intelligent request routing and delegation
- **Conditional Logic**: Rule-based processing and branching

### ADK Agent (Port 8083)
- **Data Transformation**: Format conversion and data restructuring
- **Data Analysis**: Statistical analysis and pattern recognition
- **Data Validation**: Quality checks and integrity verification
- **Data Aggregation**: Summarization and grouping operations

## 🔧 Management Commands

```bash
# Start all agents
./scripts/start-agents.sh

# Stop all agents
./scripts/stop-agents.sh

# Run tests
./scripts/test-agents.sh

# View logs
./scripts/logs.sh                 # All agents
./scripts/logs.sh crewai          # Specific agent
./scripts/logs.sh langraph -f     # Follow logs
```

## 🌐 API Endpoints

Each agent exposes identical REST APIs:

### Standard Endpoints
- `GET /health` - Health check
- `GET /capabilities` - Agent capabilities
- `GET /spec` - API specification
- `POST /execute` - Task execution

### A2A Communication
- `POST /a2a/message` - Agent-to-Agent messaging

### Example Usage
```bash
# Check agent health
curl http://localhost:8080/health

# Get capabilities
curl http://localhost:8082/capabilities

# Execute task
curl -X POST http://localhost:8083/execute \
  -H "Content-Type: application/json" \
  -d '{
    "task_type": "data_analysis",
    "description": "Analyze sales data trends",
    "context": {"period": "Q4_2024"}
  }'
```

## 🤝 Agent Collaboration

Agents can collaborate through the A2A protocol:

```bash
# Research with decision support
curl -X POST http://localhost:8080/execute \
  -H "Content-Type: application/json" \
  -d '{
    "task_type": "research", 
    "description": "Market analysis for new product",
    "collaborators": {
      "decision_maker": "http://langraph-agent:8082",
      "data_processor": "http://adk-agent:8083"
    }
  }'
```

## 📊 Monitoring

### View System Status
```bash
# Check all containers
docker-compose ps

# View resource usage
docker stats

# Check agent health
curl http://localhost:8080/health
curl http://localhost:8082/health  
curl http://localhost:8083/health
```

### Logs
```bash
# Real-time logs for all agents
docker-compose logs -f

# Logs for specific agent
docker-compose logs -f crewai-agent
docker-compose logs -f langraph-agent
docker-compose logs -f adk-agent
```

## 🔧 Development

### Project Structure
```
├── agents/
│   ├── crewai-agent/          # CrewAI research agent
│   ├── langraph-agent/        # LangGraph decision agent  
│   └── adk-agent/             # ADK data processing agent
├── tests/
│   ├── test_a2a_communication.py  # A2A testing
│   ├── test_crewai_agent.py       # Individual agent tests
│   ├── test_langraph_agent.py
│   └── test_adk_agent.py
├── scripts/                   # Management scripts
├── docker-compose.yml         # Multi-agent orchestration
└── README.md
```

### Adding New Agents
1. Create new agent directory with standard structure
2. Implement A2A protocol using `a2a_client.py`
3. Add to `docker-compose.yml`
4. Update test scripts

### Custom Configuration
Edit `docker-compose.yml` to modify:
- Port mappings
- Environment variables
- Resource limits
- Health check settings

## 🚢 Deployment

### Local Development
Use Docker Compose (this setup)

### Production Deployment
- **Cloud Run**: Deploy each agent as separate service
- **Kubernetes**: Use provided manifests
- **Docker Swarm**: Modify compose file for swarm mode

## 🧪 Testing

### Automated Tests
```bash
./scripts/test-agents.sh
```

### Manual Testing
```bash
# Python A2A testing
python tests/test_a2a_communication.py

# Individual agent testing
python tests/test_crewai_agent.py
python tests/test_langraph_agent.py
python tests/test_adk_agent.py
```

## 🐛 Troubleshooting

### Common Issues

**Agents won't start:**
```bash
# Check logs
./scripts/logs.sh

# Verify .env files have GOOGLE_API_KEY
grep GOOGLE_API_KEY */·env
```

**Port conflicts:**
```bash
# Check what's using ports
lsof -i :8080,8082,8083

# Stop conflicting services
./scripts/stop-agents.sh
```

**A2A communication fails:**
```bash
# Check network connectivity
docker network ls
docker network inspect multi-agent-system_agent-network
```

### Reset System
```bash
# Complete reset
docker-compose down -v --rmi all
./scripts/start-agents.sh
```

