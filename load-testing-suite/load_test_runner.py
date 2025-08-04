# load_test_runner.py - Updated with 3-level testing
"""
Enhanced Load Test Runner with 3-level testing system
"""

import asyncio
import os
import json
import redis
import uvicorn
from datetime import datetime
from typing import Dict, List, Optional
from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel

# Import test modules
from basic_tests import run_basic_tests
from functional_tests import run_functional_tests
from workflow_tests import run_workflow_tests

# Configuration
CREWAI_URL = os.getenv("CREWAI_URL", "https://crewai-agent-REPLACE.run.app")
LANGRAPH_URL = os.getenv("LANGRAPH_URL", "https://langraph-agent-REPLACE.run.app")
ADK_URL = os.getenv("ADK_URL", "https://adk-agent-REPLACE.run.app")
REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379")
TEST_LEVEL = int(os.getenv("TEST_LEVEL", "1"))

app = FastAPI(title="3-Level Agent Load Tester API", version="2.0.0")

# Redis connection
try:
    redis_client = redis.from_url(REDIS_URL, decode_responses=True)
except Exception as e:
    print(f"Redis connection failed: {e}")
    redis_client = None

# Global test state
current_test_status = {"running": False, "test_id": None, "level": None}

class TestConfig(BaseModel):
    test_name: str = "default_test"
    test_level: int = 1
    crewai_url: Optional[str] = None
    langraph_url: Optional[str] = None
    adk_url: Optional[str] = None

class TestStatus(BaseModel):
    running: bool
    test_id: Optional[str]
    test_level: Optional[int]
    progress: str
    total_requests_sent: int = 0
    current_test: str = ""

@app.get("/")
async def root():
    return {
        "service": "3-Level Agent Load Tester",
        "status": "ready",
        "test_levels": {
            "1": "Basic Tests (9 requests)",
            "2": "Functional Tests (12-15 requests)",
            "3": "Workflow Tests (15-18 requests)"
        },
        "endpoints": {
            "start_test": "/test/start",
            "status": "/test/status",
            "results": "/test/results/{test_id}",
            "config": "/config"
        }
    }

@app.get("/config")
async def get_config():
    """Get current configuration"""
    return {
        "agent_urls": {
            "crewai": CREWAI_URL,
            "langraph": LANGRAPH_URL,
            "adk": ADK_URL
        },
        "redis_connected": redis_client is not None,
        "test_levels_available": [1, 2, 3],
        "default_test_level": TEST_LEVEL,
        "test_status": current_test_status
    }

@app.post("/test/start")
async def start_test(config: TestConfig, background_tasks: BackgroundTasks):
    """Start a test at specified level"""
    if current_test_status["running"]:
        raise HTTPException(status_code=400, detail="Test already running")
    
    # Validate test level
    if config.test_level not in [1, 2, 3]:
        raise HTTPException(status_code=400, detail="Test level must be 1, 2, or 3")
    
    # Generate test ID
    test_id = f"test_L{config.test_level}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    # Update agent URLs if provided
    agent_urls = {
        "crewai": config.crewai_url or CREWAI_URL,
        "langraph": config.langraph_url or LANGRAPH_URL,
        "adk": config.adk_url or ADK_URL
    }
    
    # Validate URLs
    for name, url in agent_urls.items():
        if "REPLACE" in url:
            raise HTTPException(
                status_code=400,
                detail=f"Please provide valid URL for {name} agent"
            )
    
    # Start test in background
    background_tasks.add_task(run_level_test, test_id, config, agent_urls)
    
    current_test_status["running"] = True
    current_test_status["test_id"] = test_id
    current_test_status["level"] = config.test_level
    
    return {
        "test_id": test_id,
        "test_level": config.test_level,
        "status": "started",
        "estimated_requests": get_estimated_requests(config.test_level),
        "config": config.dict(),
        "agent_urls": agent_urls
    }

@app.get("/test/status")
async def get_test_status():
    """Get current test status"""
    if redis_client and current_test_status["test_id"]:
        test_id = current_test_status["test_id"]
        status_data = redis_client.get(f"test_status:{test_id}")
        
        if status_data:
            detailed_status = json.loads(status_data)
            return TestStatus(**detailed_status, **current_test_status)
    
    return TestStatus(**current_test_status, progress="Unknown")

@app.get("/test/results/{test_id}")
async def get_test_results(test_id: str):
    """Get test results by ID"""
    if redis_client:
        results_data = redis_client.get(f"test_results:{test_id}")
        if results_data:
            return json.loads(results_data)
    
    # Fallback to file system
    results_file = f"/app/results/load_test_results_{test_id}.json"
    if os.path.exists(results_file):
        with open(results_file, 'r') as f:
            return json.load(f)
    
    raise HTTPException(status_code=404, detail="Test results not found")

@app.get("/test/results")
async def list_test_results():
    """List all available test results"""
    results = []
    
    # Check Redis
    if redis_client:
        for key in redis_client.scan_iter("test_results:*"):
            test_id = key.replace("test_results:", "")
            level = extract_level_from_test_id(test_id)
            results.append({"test_id": test_id, "level": level, "source": "redis"})
    
    # Check file system
    results_dir = "/app/results"
    if os.path.exists(results_dir):
        for filename in os.listdir(results_dir):
            if filename.startswith("load_test_results_") and filename.endswith(".json"):
                test_id = filename.replace("load_test_results_", "").replace(".json", "")
                level = extract_level_from_test_id(test_id)
                if not any(r["test_id"] == test_id for r in results):
                    results.append({"test_id": test_id, "level": level, "source": "file"})
    
    return {"test_results": results}

async def run_level_test(test_id: str, config: TestConfig, agent_urls: Dict[str, str]):
    """Run test at specified level"""
    try:
        update_test_status(test_id, "initializing", 0, f"Starting Level {config.test_level} test")
        
        start_time = datetime.now()
        
        # Run appropriate test level
        if config.test_level == 1:
            update_test_status(test_id, "running", 0, "Running basic tests")
            test_results = await run_basic_tests(agent_urls)
        elif config.test_level == 2:
            update_test_status(test_id, "running", 0, "Running functional tests")
            test_results = await run_functional_tests(agent_urls)
        elif config.test_level == 3:
            update_test_status(test_id, "running", 0, "Running workflow tests")
            test_results = await run_workflow_tests(agent_urls)
        else:
            raise ValueError(f"Invalid test level: {config.test_level}")
        
        # Add test metadata
        test_results.update({
            "test_id": test_id,
            "test_name": config.test_name,
            "test_level": config.test_level,
            "start_time": start_time.isoformat(),
            "end_time": datetime.now().isoformat(),
            "config": config.dict(),
            "agent_urls": agent_urls
        })
        
        # Save results
        save_test_results(test_id, test_results)
        
        update_test_status(test_id, "completed", len(test_results.get("results", [])), "Test completed successfully")
        
    except Exception as e:
        error_msg = f"Level {config.test_level} test failed: {str(e)}"
        update_test_status(test_id, "failed", 0, error_msg)
        print(f"Test {test_id} failed: {e}")
    
    finally:
        current_test_status["running"] = False
        current_test_status["test_id"] = None
        current_test_status["level"] = None

def save_test_results(test_id: str, test_results: Dict):
    """Save test results to Redis and file"""
    # Save to Redis
    if redis_client:
        redis_client.set(
            f"test_results:{test_id}",
            json.dumps(test_results),
            ex=86400  # Expire after 24 hours
        )
    
    # Save to file
    os.makedirs("/app/results", exist_ok=True)
    with open(f"/app/results/load_test_results_{test_id}.json", 'w') as f:
        json.dump(test_results, f, indent=2)

def update_test_status(test_id: str, status: str, requests_sent: int, current_test: str):
    """Update test status in Redis"""
    status_data = {
        "progress": status,
        "total_requests_sent": requests_sent,
        "current_test": current_test,
        "timestamp": datetime.now().isoformat()
    }
    
    if redis_client:
        redis_client.set(
            f"test_status:{test_id}",
            json.dumps(status_data),
            ex=3600  # Expire after 1 hour
        )

def get_estimated_requests(level: int) -> int:
    """Get estimated request count for test level"""
    estimates = {1: 9, 2: 15, 3: 18}
    return estimates.get(level, 9)

def extract_level_from_test_id(test_id: str) -> int:
    """Extract test level from test ID"""
    try:
        if "_L" in test_id:
            return int(test_id.split("_L")[1].split("_")[0])
    except:
        pass
    return 1

@app.on_event("startup")
async def startup_event():
    print("3-Level Agent Load Tester started")
    print(f"Agent URLs:")
    print(f"  CrewAI: {CREWAI_URL}")
    print(f"  LangGraph: {LANGRAPH_URL}")
    print(f"  ADK: {ADK_URL}")
    print(f"Redis: {'Connected' if redis_client else 'Not connected'}")
    print(f"Default test level: {TEST_LEVEL}")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)