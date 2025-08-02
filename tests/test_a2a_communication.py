"""
Test A2A communication between agents

This script tests agent-to-agent communication.
Run this after starting multiple agents.
"""

import asyncio
import sys
import os

# Add agents path to import a2a_client
sys.path.append(os.path.join(os.path.dirname(__file__), '../agents/crewai-agent'))
from a2a_client import A2AClient, A2AMessage, A2AMessageType

# Agent URLs - update these based on running agents
GEMINI_AGENT_URL = "http://localhost:8080"
LANGRAPH_AGENT_URL = "http://localhost:8082"
ADK_AGENT_URL = "http://localhost:8083"

async def test_health_checks():
    """Test health checks between agents"""
    print("Testing A2A health checks...")
    
    client = A2AClient("test-client", "test")
    
    agents = {
        "Gemini": GEMINI_AGENT_URL,
        "LangGraph": LANGRAPH_AGENT_URL,
        "ADK": ADK_AGENT_URL
    }
    
    for name, url in agents.items():
        try:
            response = await client.health_check(url)
            if response.success:
                status = response.payload.get("status", "unknown")
                agent_id = response.payload.get("agent_id", "unknown")
                print(f"  {name} Agent ({agent_id}): {status}")
            else:
                print(f"  {name} Agent: {response.error}")
        except Exception as e:
            print(f"  {name} Agent: Connection failed - {e}")
    
    print()

async def test_capabilities_discovery():
    """Test discovering capabilities from each agent"""
    print("Testing capabilities discovery...")
    
    client = A2AClient("test-client", "test")
    
    agents = {
        "Gemini": GEMINI_AGENT_URL,
        "LangGraph": LANGRAPH_AGENT_URL,
        "ADK": ADK_AGENT_URL
    }
    
    for name, url in agents.items():
        try:
            response = await client.get_capabilities(url)
            if response.success:
                capabilities = response.payload.get("capabilities", [])
                print(f"  {name} Agent capabilities:")
                for cap in capabilities:
                    print(f"    - {cap.get('name', 'unknown')}: {cap.get('description', '')}")
            else:
                print(f"  {name} Agent capabilities: {response.error}")
        except Exception as e:
            print(f"  {name} Agent: Connection failed - {e}")
    
    print()

async def test_basic_task_delegation():
    """Test basic task delegation (with fake API keys, will fail gracefully)"""
    print("Testing basic task delegation...")
    
    client = A2AClient("test-client", "test")
    
    # Test 1: Ask Gemini agent to execute a research task
    print("  Test 1: Research task to Gemini agent")
    task_data = {
        "task_type": "research",
        "description": "Test research task",
        "context": {"test": True}
    }
    
    try:
        response = await client.execute_task(GEMINI_AGENT_URL, task_data)
        if response.success:
            task_result = response.payload.get("task_result", {})
            print(f"    Research task completed: {task_result.get('success', False)}")
        else:
            print(f"    Research task failed: {response.error}")
    except Exception as e:
        print(f"    Research task failed: {e}")
    
    # Test 2: Ask LangGraph agent to make a decision
    print("  Test 2: Decision task to LangGraph agent")
    decision_data = {
        "task_type": "decision_making",
        "description": "Test decision task",
        "context": {
            "options": ["A", "B"],
            "criteria": {"test": "value"}
        }
    }
    
    try:
        response = await client.execute_task(LANGRAPH_AGENT_URL, decision_data)
        if response.success:
            task_result = response.payload.get("task_result", {})
            print(f"    Decision task completed: {task_result.get('success', False)}")
        else:
            print(f"    Decision task failed: {response.error}")
    except Exception as e:
        print(f"    Decision task failed: {e}")
    
    # Test 3: Ask ADK agent to process data
    print("  Test 3: Data processing task to ADK agent")
    data_task = {
        "task_type": "data_transformation",
        "description": "Test data transformation",
        "context": {
            "data": {
                "records": [
                    {"name": "test", "value": 123}
                ]
            },
            "target_format": "json"
        }
    }
    
    try:
        response = await client.execute_task(ADK_AGENT_URL, data_task)
        if response.success:
            task_result = response.payload.get("task_result", {})
            print(f"    Data processing completed: {task_result.get('success', False)}")
        else:
            print(f"    Data processing failed: {response.error}")
    except Exception as e:
        print(f"    Data processing failed: {e}")
    
    print()

async def main():
    """Run all A2A tests"""
    print("Starting A2A Communication Tests\n")
    
    try:
        await test_health_checks()
        await test_capabilities_discovery()
        await test_basic_task_delegation()
        
        print("A2A tests completed!")
        
    except Exception as e:
        print(f"A2A tests failed: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit_code = asyncio.run(main())