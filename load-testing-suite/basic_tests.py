"""
Level 1: Basic Tests
Agent discovery, health checks, basic endpoints
Target: 9 requests total
"""
import asyncio
import httpx
import time
import json
from typing import Dict, List, Any
from dataclasses import dataclass
from datetime import datetime


@dataclass
class BasicTestResult:
    test_name: str
    agent_name: str
    success: bool
    response_time: float
    status_code: int
    result_data: Dict[str, Any]
    error: str = ""


class BasicTester:
    def __init__(self, agent_urls: Dict[str, str]):
        self.agent_urls = agent_urls
        self.results = []
        self.timeout = 15.0
    
    async def run_all_basic_tests(self) -> List[BasicTestResult]:
        """Run all basic tests - 9 requests total"""
        print("Starting Level 1: Basic Tests")
        
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            health_results = await self.health_check_test(client)
            spec_results = await self.agent_spec_test(client) 
            capabilities_results = await self.capabilities_test(client)
            
            all_results = health_results + spec_results + capabilities_results
            self.results.extend(all_results)
            return all_results
    
    async def health_check_test(self, client: httpx.AsyncClient) -> List[BasicTestResult]:
        """Test /health endpoints - 3 requests"""
        results = []
        
        for agent_name, url in self.agent_urls.items():
            start_time = time.time()
            
            try:
                response = await client.get(f"{url}/health")
                response_time = time.time() - start_time
                
                if response.status_code == 200:
                    health_data = response.json()
                    
                    results.append(BasicTestResult(
                        test_name="health_check",
                        agent_name=agent_name,
                        success=True,
                        response_time=response_time,
                        status_code=response.status_code,
                        result_data=health_data
                    ))
                else:
                    results.append(BasicTestResult(
                        test_name="health_check",
                        agent_name=agent_name,
                        success=False,
                        response_time=response_time,
                        status_code=response.status_code,
                        result_data={},
                        error=f"HTTP {response.status_code}"
                    ))
                    
            except Exception as e:
                response_time = time.time() - start_time
                results.append(BasicTestResult(
                    test_name="health_check",
                    agent_name=agent_name,
                    success=False,
                    response_time=response_time,
                    status_code=0,
                    result_data={},
                    error=str(e)
                ))
            
            await asyncio.sleep(1)
        
        return results
    
    async def agent_spec_test(self, client: httpx.AsyncClient) -> List[BasicTestResult]:
        """Test /spec endpoints - 3 requests"""
        results = []
        
        for agent_name, url in self.agent_urls.items():
            start_time = time.time()
            
            try:
                response = await client.get(f"{url}/spec")
                response_time = time.time() - start_time
                
                if response.status_code == 200:
                    spec_data = response.json()
                    
                    required_fields = ["agent_id", "agent_type", "supported_task_types"]
                    has_required = all(field in spec_data for field in required_fields)
                    
                    results.append(BasicTestResult(
                        test_name="agent_spec",
                        agent_name=agent_name,
                        success=has_required,
                        response_time=response_time,
                        status_code=response.status_code,
                        result_data=spec_data,
                        error="" if has_required else "Missing required spec fields"
                    ))
                else:
                    results.append(BasicTestResult(
                        test_name="agent_spec",
                        agent_name=agent_name,
                        success=False,
                        response_time=response_time,
                        status_code=response.status_code,
                        result_data={},
                        error=f"HTTP {response.status_code}"
                    ))
                    
            except Exception as e:
                response_time = time.time() - start_time
                results.append(BasicTestResult(
                    test_name="agent_spec",
                    agent_name=agent_name,
                    success=False,
                    response_time=response_time,
                    status_code=0,
                    result_data={},
                    error=str(e)
                ))
            
            await asyncio.sleep(1)
        
        return results
    
    async def capabilities_test(self, client: httpx.AsyncClient) -> List[BasicTestResult]:
        """Test /capabilities endpoints - 3 requests"""
        results = []
        
        for agent_name, url in self.agent_urls.items():
            start_time = time.time()
            
            try:
                response = await client.get(f"{url}/capabilities")
                response_time = time.time() - start_time
                
                if response.status_code == 200:
                    capabilities_data = response.json()
                    
                    has_capabilities = isinstance(capabilities_data, list) and len(capabilities_data) > 0
                    
                    results.append(BasicTestResult(
                        test_name="capabilities",
                        agent_name=agent_name,
                        success=has_capabilities,
                        response_time=response_time,
                        status_code=response.status_code,
                        result_data={"capabilities_count": len(capabilities_data)},
                        error="" if has_capabilities else "No capabilities returned"
                    ))
                else:
                    results.append(BasicTestResult(
                        test_name="capabilities",
                        agent_name=agent_name,
                        success=False,
                        response_time=response_time,
                        status_code=response.status_code,
                        result_data={},
                        error=f"HTTP {response.status_code}"
                    ))
                    
            except Exception as e:
                response_time = time.time() - start_time
                results.append(BasicTestResult(
                    test_name="capabilities",
                    agent_name=agent_name,
                    success=False,
                    response_time=response_time,
                    status_code=0,
                    result_data={},
                    error=str(e)
                ))
            
            await asyncio.sleep(1)
        
        return results
    
    def analyze_basic_results(self, results: List[BasicTestResult]) -> Dict[str, Any]:
        """Analyze basic test results"""
        if not results:
            return {"error": "No basic test results"}
        
        total_tests = len(results)
        successful_tests = len([r for r in results if r.success])
        
        by_agent = {}
        by_test = {}
        
        for result in results:
            if result.agent_name not in by_agent:
                by_agent[result.agent_name] = {"total": 0, "success": 0, "avg_time": 0}
            by_agent[result.agent_name]["total"] += 1
            if result.success:
                by_agent[result.agent_name]["success"] += 1
            
            if result.test_name not in by_test:
                by_test[result.test_name] = {"total": 0, "success": 0, "avg_time": 0}
            by_test[result.test_name]["total"] += 1
            if result.success:
                by_test[result.test_name]["success"] += 1
        
        for agent_name, stats in by_agent.items():
            agent_results = [r for r in results if r.agent_name == agent_name]
            response_times = [r.response_time for r in agent_results if r.success]
            stats["avg_time"] = sum(response_times) / len(response_times) if response_times else 0
        
        for test_name, stats in by_test.items():
            test_results = [r for r in results if r.test_name == test_name]
            response_times = [r.response_time for r in test_results if r.success]
            stats["avg_time"] = sum(response_times) / len(response_times) if response_times else 0
        
        return {
            "total_tests": total_tests,
            "successful_tests": successful_tests,
            "success_rate": (successful_tests / total_tests * 100) if total_tests > 0 else 0,
            "by_agent": by_agent,
            "by_test_type": by_test
        }


async def run_basic_tests(agent_urls: Dict[str, str]) -> Dict[str, Any]:
    """Main function to run basic tests"""
    tester = BasicTester(agent_urls)
    
    start_time = time.time()
    results = await tester.run_all_basic_tests()
    total_time = time.time() - start_time
    
    analysis = tester.analyze_basic_results(results)
    
    return {
        "test_type": "basic_tests",
        "timestamp": datetime.utcnow().isoformat(),
        "execution_time": total_time,
        "results": [
            {
                "test_name": r.test_name,
                "agent_name": r.agent_name,
                "success": r.success,
                "response_time": r.response_time,
                "status_code": r.status_code,
                "error": r.error,
                "result_data": r.result_data
            } for r in results
        ],
        "analysis": analysis
    }