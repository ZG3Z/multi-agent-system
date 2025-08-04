# load_test_runner.py
"""
Load Test Runner with FastAPI interface
Provides REST API to control and monitor testing
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
from minimal_load_testing import MinimalLoadTester, TestResult

# Configuration from environment
CREWAI_URL = os.getenv("CREWAI_URL", "https://crewai-agent-REPLACE.run.app")
LANGRAPH_URL = os.getenv("LANGRAPH_URL", "https://langraph-agent-REPLACE.run.app")
ADK_URL = os.getenv("ADK_URL", "https://adk-agent-REPLACE.run.app")
REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379")

app = FastAPI(title="Agent Load Tester API", version="1.0.0")

# Redis connection
try:
    redis_client = redis.from_url(REDIS_URL, decode_responses=True)
except Exception as e:
    print(f"Redis connection failed: {e}")
    redis_client = None

# Global test state
current_test_status = {"running": False, "test_id": None}

class TestConfig(BaseModel):
    test_name: str = "default_test"
    crewai_url: Optional[str] = None
    langraph_url: Optional[str] = None
    adk_url: Optional[str] = None
    run_health_check: bool = True
    run_capabilities: bool = True
    run_a2a_test: bool = True
    run_collaboration_test: bool = True  # New collaboration test
    run_latency_test: bool = True
    run_task_test: bool = False  # Disabled by default to save API calls
    latency_requests_per_agent: int = 3

class TestStatus(BaseModel):
    running: bool
    test_id: Optional[str]
    progress: str
    total_requests_sent: int = 0
    current_test: str = ""

@app.get("/")
async def root():
    return {
        "service": "Agent Load Tester",
        "status": "ready",
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
        "test_status": current_test_status
    }

@app.post("/test/start")
async def start_test(config: TestConfig, background_tasks: BackgroundTasks):
    """Start a new load test"""
    if current_test_status["running"]:
        raise HTTPException(status_code=400, detail="Test already running")
    
    # Generate test ID
    test_id = f"test_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
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
    background_tasks.add_task(run_load_test, test_id, config, agent_urls)
    
    current_test_status["running"] = True
    current_test_status["test_id"] = test_id
    
    return {
        "test_id": test_id,
        "status": "started",
        "config": config.dict(),
        "agent_urls": agent_urls
    }

@app.get("/test/status")
async def get_test_status():
    """Get current test status"""
    if redis_client and current_test_status["test_id"]:
        # Get detailed status from Redis
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
            results.append({"test_id": test_id, "source": "redis"})
    
    # Check file system
    results_dir = "/app/results"
    if os.path.exists(results_dir):
        for filename in os.listdir(results_dir):
            if filename.startswith("load_test_results_") and filename.endswith(".json"):
                test_id = filename.replace("load_test_results_", "").replace(".json", "")
                if not any(r["test_id"] == test_id for r in results):
                    results.append({"test_id": test_id, "source": "file"})
    
    return {"test_results": results}

async def run_load_test(test_id: str, config: TestConfig, agent_urls: Dict[str, str]):
    """Run the actual load test"""
    try:
        # Update status
        update_test_status(test_id, "initializing", 0, "Setting up test")
        
        # Create tester
        tester = MinimalLoadTester(agent_urls)
        all_results = []
        total_requests = 0
        
        # Estimate total requests
        estimated_requests = 0
        if config.run_health_check: estimated_requests += 3
        if config.run_capabilities: estimated_requests += 3
        if config.run_a2a_test: estimated_requests += 3
        if config.run_collaboration_test: estimated_requests += 6  # Collaboration scenarios
        if config.run_latency_test: estimated_requests += 3 * config.latency_requests_per_agent
        if config.run_task_test: estimated_requests += 3
        
        try:
            # Run selected tests
            if config.run_health_check:
                update_test_status(test_id, "running", total_requests, "Health check test")
                results = await tester.health_check_test()
                all_results.extend(results)
                total_requests += len(results)
                await asyncio.sleep(2)
            
            if config.run_capabilities:
                update_test_status(test_id, "running", total_requests, "Capabilities test")
                results = await tester.capabilities_test()
                all_results.extend(results)
                total_requests += len(results)
                await asyncio.sleep(2)
            
            if config.run_a2a_test:
                update_test_status(test_id, "running", total_requests, "A2A communication test")
                results = await tester.a2a_communication_test()
                all_results.extend(results)
                total_requests += len(results)
                await asyncio.sleep(3)
            
            if config.run_collaboration_test:
                update_test_status(test_id, "running", total_requests, "Agent collaboration test")
                results = await tester.collaboration_test()
                all_results.extend(results)
                total_requests += len(results)
                await asyncio.sleep(5)  # Longer delay for collaboration
            
            if config.run_latency_test:
                update_test_status(test_id, "running", total_requests, "Latency test")
                results = await tester.latency_test(config.latency_requests_per_agent)
                all_results.extend(results)
                total_requests += len(results)
                await asyncio.sleep(3)
            
            if config.run_task_test:
                update_test_status(test_id, "running", total_requests, "Basic task test")
                results = await tester.basic_task_test()
                all_results.extend(results)
                total_requests += len(results)
            
            # Analyze results
            update_test_status(test_id, "analyzing", total_requests, "Analyzing results")
            analysis = tester.analyze_results(all_results)
            
            # Save results
            test_results = {
                "test_id": test_id,
                "test_name": config.test_name,
                "timestamp": datetime.now().isoformat(),
                "config": config.dict(),
                "agent_urls": agent_urls,
                "total_requests": len(all_results),
                "results": [result.__dict__ for result in all_results],
                "analysis": analysis
            }
            
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
            
            # Final status
            update_test_status(test_id, "completed", total_requests, "Test completed successfully")
            
        finally:
            await tester.close()
            
    except Exception as e:
        error_msg = f"Test failed: {str(e)}"
        update_test_status(test_id, "failed", total_requests, error_msg)
        print(f"Test {test_id} failed: {e}")
    
    finally:
        # Reset global status
        current_test_status["running"] = False
        current_test_status["test_id"] = None

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

@app.on_event("startup")
async def startup_event():
    print("Agent Load Tester started")
    print(f"Agent URLs:")
    print(f"  CrewAI: {CREWAI_URL}")
    print(f"  LangGraph: {LANGRAPH_URL}")
    print(f"  ADK: {ADK_URL}")
    print(f"Redis: {'Connected' if redis_client else 'Not connected'}")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)