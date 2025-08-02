import time
import uvicorn
import logging
from datetime import datetime
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List

from models import TaskRequest, TaskResult, AgentCapability, AgentStatus
from agent_logic import ADKLogic
from config import Config
from a2a_client import A2AClient, A2AMessageHandler, A2AMessage, A2AResponse

# Global variables
agent_logic = None
a2a_client = None
a2a_handler = None
start_time = time.time()
active_tasks = 0

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    global agent_logic, a2a_client, a2a_handler
    agent_logic = ADKLogic()
    a2a_client = A2AClient(Config.AGENT_ID, Config.AGENT_TYPE)
    a2a_handler = A2AMessageHandler(Config.AGENT_ID, Config.AGENT_TYPE)
    logging.info(f"ADK Agent with A2A started on {Config.HOST}:{Config.PORT}")
    yield
    # Shutdown
    logging.info("ADK Agent shutting down")

app = FastAPI(
    title="ADK Agent with A2A",
    description="ADK-powered data processing agent with A2A communication capabilities",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/execute", response_model=TaskResult)
async def execute_task(request: TaskRequest):
    """Main task execution endpoint"""
    global active_tasks
    
    try:
        active_tasks += 1
        logging.info(f"Executing {request.task_type} task: {request.description[:100]}...")
        
        # Execute task with ADK
        result = await agent_logic.execute_task(
            task_type=request.task_type,
            description=request.description,
            context=request.context
        )
        
        # Handle collaborators with A2A communication
        if request.collaborators:
            logging.info(f"Using A2A to collaborate with: {list(request.collaborators.keys())}")
            
            # Example: Get research context from Gemini agent
            if "researcher" in request.collaborators:
                researcher_url = request.collaborators["researcher"]
                research_request = {
                    "task_type": "research",
                    "description": f"Research context for data processing: {request.description}",
                    "context": {"data_processing_context": result.get("result", {})}
                }
                
                research_response = await a2a_client.execute_task(researcher_url, research_request)
                if research_response.success:
                    result["result"]["collaboration"] = {
                        "researcher": research_response.payload.get("task_result", {})
                    }
            
            # Example: Get decision guidance from LangGraph agent
            if "decision_maker" in request.collaborators:
                decision_maker_url = request.collaborators["decision_maker"]
                decision_request = {
                    "task_type": "decision_making",
                    "description": f"Make decision about data processing approach: {request.description}",
                    "context": {"processing_options": result.get("result", {})}
                }
                
                decision_response = await a2a_client.execute_task(decision_maker_url, decision_request)
                if decision_response.success:
                    result["result"]["collaboration"] = result["result"].get("collaboration", {})
                    result["result"]["collaboration"]["decision_maker"] = decision_response.payload.get("task_result", {})
        
        return TaskResult(
            success=result["success"],
            result=result.get("result", {}),
            execution_time=result["execution_time"],
            error=result.get("error")
        )
        
    except Exception as e:
        logging.error(f"Task execution failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    
    finally:
        active_tasks -= 1

@app.get("/capabilities", response_model=List[AgentCapability])
async def get_capabilities():
    """Get agent capabilities"""
    return agent_logic.get_capabilities()

@app.get("/health", response_model=AgentStatus)
async def health_check():
    """Health check endpoint"""
    uptime = time.time() - start_time
    capabilities = agent_logic.get_capabilities()
    
    return AgentStatus(
        uptime=uptime,
        active_tasks=active_tasks,
        capabilities_count=len(capabilities)
    )

@app.post("/a2a/message", response_model=A2AResponse)
async def handle_a2a_message(message: A2AMessage):
    """Handle incoming A2A messages from other agents"""
    try:
        response = await a2a_handler.handle_message(message, agent_logic)
        return response
    except Exception as e:
        logging.error(f"A2A message handling failed: {e}")
        return A2AResponse(
            success=False,
            message_id=message.message_id,
            sender_id=Config.AGENT_ID,
            error=f"Message handling failed: {str(e)}",
            timestamp=datetime.utcnow().isoformat()
        )

@app.get("/spec")
async def get_spec():
    """API specification"""
    return {
        "agent_id": Config.AGENT_ID,
        "agent_name": Config.AGENT_NAME,
        "agent_type": Config.AGENT_TYPE,
        "version": "1.0.0",
        "endpoints": {
            "execute": "/execute",
            "capabilities": "/capabilities", 
            "health": "/health",
            "spec": "/spec",
            "docs": "/docs"
        },
        "supported_task_types": ["data_transformation", "data_analysis", "data_validation", "data_aggregation"],
        "a2a_ready": True,
        "a2a_endpoint": "/a2a/message"
    }

if __name__ == "__main__":
    logging.basicConfig(level=Config.LOG_LEVEL)
    uvicorn.run(
        app,
        host=Config.HOST,
        port=Config.PORT,
        reload=False
    )