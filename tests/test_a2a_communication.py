"""
Test A2A communication between agents

This script tests agent-to-agent communication.
Run this after starting multiple agents.
"""

import asyncio
import sys
import os

# Add agents path to import a2a_client
sys.path.append('../agents/crewai-agent')
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

async def test_task_delegation():
    """Test delegating tasks between agents"""
    print("Testing task delegation...")
    
    client = A2AClient("test-client", "test")
    
    # Test 1: Ask Gemini agent to execute a research task
    print("  Test 1: Research task to Gemini agent")
    task_data = {
        "task_type": "research",
        "description": "Research the benefits of microservices architecture",
        "context": {"focus": "scalability and maintenance"}
    }
    
    try:
        response = await client.execute_task(GEMINI_AGENT_URL, task_data)
        if response.success:
            task_result = response.payload.get("task_result", {})
            print(f"    Research completed: {task_result.get('success', False)}")
            if task_result.get("result", {}).get("summary"):
                print(f"    Summary: {task_result['result']['summary'][:100]}...")
        else:
            print(f"    Research failed: {response.error}")
    except Exception as e:
        print(f"    Research failed: {e}")
    
    # Test 2: Ask LangGraph agent to make a decision
    print("  Test 2: Decision task to LangGraph agent")
    decision_data = {
        "task_type": "decision_making",
        "description": "Choose the best deployment strategy",
        "context": {
            "options": ["Docker Swarm", "Kubernetes", "Cloud Run"],
            "criteria": {"simplicity": "high", "scalability": "medium"}
        }
    }
    
    try:
        response = await client.execute_task(LANGRAPH_AGENT_URL, decision_data)
        if response.success:
            task_result = response.payload.get("task_result", {})
            print(f"    Decision completed: {task_result.get('success', False)}")
            if task_result.get("result", {}).get("decision"):
                decision = task_result['result']['decision']
                confidence = task_result['result'].get('confidence', 0)
                print(f"    Decision: {decision} (confidence: {confidence})")
        else:
            print(f"    Decision failed: {response.error}")
    except Exception as e:
        print(f"    Decision failed: {e}")
    
    # Test 3: Ask ADK agent to process data
    print("  Test 3: Data processing task to ADK agent")
    data_task = {
        "task_type": "data_transformation",
        "description": "Transform customer data for analysis",
        "context": {
            "data": {
                "records": [
                    {"name": "Alice", "age": 30, "score": 85},
                    {"name": "Bob", "age": 25, "score": 92}
                ]
            },
            "target_format": "json",
            "transformations": ["normalize_columns"]
        }
    }
    
    try:
        response = await client.execute_task(ADK_AGENT_URL, data_task)
        if response.success:
            task_result = response.payload.get("task_result", {})
            print(f"    Data processing completed: {task_result.get('success', False)}")
            if task_result.get("result", {}).get("data_shape"):
                shape = task_result['result']['data_shape']
                print(f"    Data shape: {shape}")
        else:
            print(f"    Data processing failed: {response.error}")
    except Exception as e:
        print(f"    Data processing failed: {e}")
    
    print()

async def test_agent_collaboration():
    """Test collaborative workflow between multiple agents"""
    print("Testing multi-agent collaboration...")
    
    client = A2AClient("test-client", "test")
    
    # Scenario: Research + Decision + Data Processing pipeline
    print("  Scenario: Research -> Decision -> Data Processing pipeline")
    
    # Step 1: Research task
    print("    Step 1: Research phase...")
    research_task = {
        "task_type": "research",
        "description": "Research customer satisfaction metrics",
        "context": {"industry": "SaaS", "focus": "retention"}
    }
    
    research_response = await client.execute_task(GEMINI_AGENT_URL, research_task)
    research_result = None
    
    if research_response.success:
        research_result = research_response.payload.get("task_result", {})
        print(f"      Research completed")
    else:
        print(f"      Research failed: {research_response.error}")
        return
    
    # Step 2: Decision based on research
    print("    Step 2: Decision phase...")
    decision_task = {
        "task_type": "decision_making",
        "description": "Choose the best metrics to track",
        "context": {
            "research_findings": research_result.get("result", {}),
            "options": ["NPS", "CSAT", "CES", "Retention Rate"],
            "criteria": {"accuracy": "high", "actionability": "high"}
        }
    }
    
    decision_response = await client.execute_task(LANGRAPH_AGENT_URL, decision_task)
    decision_result = None
    
    if decision_response.success:
        decision_result = decision_response.payload.get("task_result", {})
        print(f"      Decision completed")
    else:
        print(f"      Decision failed: {decision_response.error}")
        return
    
    # Step 3: Data processing based on decision
    print("    Step 3: Data processing phase...")
    processing_task = {
        "task_type": "data_analysis",
        "description": "Analyze customer satisfaction data",
        "context": {
            "research_context": research_result.get("result", {}),
            "decision_context": decision_result.get("result", {}),
            "data": {
                "satisfaction_scores": [8.5, 7.2, 9.1, 6.8, 8.9, 7.5, 8.3],
                "customer_segments": ["Enterprise", "SMB", "Startup"],
                "time_period": "Q4_2024"
            }
        }
    }
    
    processing_response = await client.execute_task(ADK_AGENT_URL, processing_task)
    
    if processing_response.success:
        processing_result = processing_response.payload.get("task_result", {})
        print(f"      Data processing completed")
        print(f"      Pipeline successful: Research -> Decision -> Processing")
    else:
        print(f"      Data processing failed: {processing_response.error}")
    
    print()

async def test_find_capable_agent():
    """Test finding agents with specific capabilities"""
    print("Testing agent capability search...")
    
    client = A2AClient("test-client", "test")
    
    agent_urls = [GEMINI_AGENT_URL, LANGRAPH_AGENT_URL, ADK_AGENT_URL]
    
    # Test finding agents with specific capabilities
    capabilities_to_find = [
        "research",
        "decision_making", 
        "data_transformation",
        "nonexistent_capability"
    ]
    
    for capability in capabilities_to_find:
        print(f"  Looking for capability: {capability}")
        agent_url = await client.find_capable_agent(agent_urls, capability)
        if agent_url:
            print(f"    Found at: {agent_url}")
        else:
            print(f"    Not found")
    
    print()

async def main():
    """Run all A2A tests"""
    print("Starting A2A Communication Tests\n")
    
    try:
        await test_health_checks()
        await test_capabilities_discovery()
        await test_task_delegation()
        await test_agent_collaboration()
        await test_find_capable_agent()
        
        print("All A2A tests completed!")
        
    except Exception as e:
        print(f"A2A tests failed: {e}")

if __name__ == "__main__":
    asyncio.run(main())