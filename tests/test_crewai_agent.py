"""
Individual test for Gemini (CrewAI) Agent

Usage:
    python tests/test_crewai_agent.py
"""

import asyncio
import httpx
import sys
import os

# Add path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '../agents/crewai-agent'))

BASE_URL = "http://localhost:8080"

async def test_health():
    """Test health endpoint"""
    print("Testing CrewAI Agent health...")
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

async def test_research_task():
    """Test research capability"""
    print("Testing research task...")
    
    task_request = {
        "task_type": "research",
        "description": "Research renewable energy trends in 2024",
        "context": {"focus": "solar and wind power"}
    }
    
    async with httpx.AsyncClient(timeout=300.0) as client:
        response = await client.post(f"{BASE_URL}/execute", json=task_request)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"Success: {result['success']}")
            print(f"Execution time: {result['execution_time']:.2f}s")
            
            if result['success'] and result.get('result', {}).get('summary'):
                summary = result['result']['summary']
                print(f"Summary: {summary[:150]}...")
        print()

async def test_analysis_task():
    """Test analysis capability"""
    print("Testing analysis task...")
    
    task_request = {
        "task_type": "analysis",
        "description": "Analyze market trends for electric vehicles",
        "context": {"timeframe": "2024", "regions": ["US", "EU", "China"]}
    }
    
    async with httpx.AsyncClient(timeout=300.0) as client:
        response = await client.post(f"{BASE_URL}/execute", json=task_request)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"Success: {result['success']}")
            print(f"Execution time: {result['execution_time']:.2f}s")
            
            if result['success']:
                analysis = result.get('result', {}).get('analysis', '')
                print(f"Analysis preview: {analysis[:150]}...")
        print()

async def main():
    """Run all Gemini Agent tests"""
    print("Starting Gemini Agent Individual Tests\n")
    
    try:
        await test_health()
        await test_capabilities()
        await test_research_task()
        await test_analysis_task()
        
        print("Gemini Agent tests completed!")
        
    except httpx.ConnectError:
        print("Cannot connect to Gemini Agent. Make sure it's running on localhost:8080")
    except Exception as e:
        print(f"Test failed: {e}")

if __name__ == "__main__":
    asyncio.run(main())