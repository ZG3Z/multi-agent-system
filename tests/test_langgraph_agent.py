"""
Individual test for LangGraph Agent

Usage:
    python tests/test_langraph_agent.py
"""

import asyncio
import httpx
import sys
import os

# Add path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '../agents/langraph-agent'))

BASE_URL = "http://localhost:8082"

async def test_health():
    """Test health endpoint"""
    print("Testing LangGraph Agent health...")
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BASE_URL}/health")
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Agent ID: {data.get('agent_id')}")
            print(f"Status: {data.get('status')}")
            print(f"Uptime: {data.get('uptime'):.2f}s")
        print()

async def test_capabilities():
    """Test capabilities endpoint"""
    print("Testing capabilities...")
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BASE_URL}/capabilities")
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            capabilities = response.json()
            print(f"Capabilities count: {len(capabilities)}")
            for cap in capabilities:
                print(f"  - {cap['name']}: {cap['description']}")
        print()

async def test_decision_making():
    """Test decision making capability"""
    print("Testing decision making...")
    
    task_request = {
        "task_type": "decision_making",
        "description": "Choose the best cloud provider for a startup",
        "context": {
            "options": ["AWS", "Google Cloud", "Azure"],
            "criteria": {"cost": "high", "ease_of_use": "high", "scalability": "medium"}
        }
    }
    
    async with httpx.AsyncClient(timeout=300.0) as client:
        response = await client.post(f"{BASE_URL}/execute", json=task_request)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"Success: {result['success']}")
            print(f"Execution time: {result['execution_time']:.2f}s")
            
            if result['success']:
                decision_result = result.get('result', {})
                print(f"Decision: {decision_result.get('decision', 'No decision')}")
                print(f"Confidence: {decision_result.get('confidence', 0)}")
        print()

async def test_routing():
    """Test routing capability"""
    print("Testing routing...")
    
    task_request = {
        "task_type": "routing",
        "description": "Route customer inquiry to appropriate department",
        "context": {
            "input_data": {
                "inquiry_type": "billing_issue",
                "urgency": "high",
                "customer_tier": "enterprise"
            },
            "routing_rules": {
                "billing_issue": "billing_department",
                "technical_issue": "support_department",
                "high_urgency": "escalate"
            }
        }
    }
    
    async with httpx.AsyncClient(timeout=300.0) as client:
        response = await client.post(f"{BASE_URL}/execute", json=task_request)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"Success: {result['success']}")
            print(f"Execution time: {result['execution_time']:.2f}s")
            
            if result['success']:
                routing_result = result.get('result', {})
                print(f"Route: {routing_result.get('route', 'No route')}")
                print(f"Reason: {routing_result.get('routing_reason', 'No reason')[:100]}...")
        print()

async def main():
    """Run all LangGraph Agent tests"""
    print("Starting LangGraph Agent Individual Tests\n")
    
    try:
        await test_health()
        await test_capabilities()
        await test_decision_making()
        await test_routing()
        
        print("LangGraph Agent tests completed!")
        
    except httpx.ConnectError:
        print("Cannot connect to LangGraph Agent. Make sure it's running on localhost:8082")
    except Exception as e:
        print(f"Test failed: {e}")

if __name__ == "__main__":
    asyncio.run(main())