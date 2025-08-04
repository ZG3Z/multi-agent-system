"""
Level 2: Functional Tests
A2A communication, realistic tasks, cross-agent integration
Target: 12-15 requests total
"""
import asyncio
import httpx
import time
import json
import uuid
from typing import Dict, List, Any
from dataclasses import dataclass
from datetime import datetime


@dataclass
class FunctionalTestResult:
    test_name: str
    agent_name: str
    success: bool
    response_time: float
    status_code: int
    task_data: Dict[str, Any]
    result_data: Dict[str, Any]
    error: str = ""


class FunctionalTester:
    def __init__(self, agent_urls: Dict[str, str]):
        self.agent_urls = agent_urls
        self.results = []
        self.timeout = 45.0
    
    async def run_all_functional_tests(self) -> List[FunctionalTestResult]:
        """Run all functional tests - 12-15 requests total"""
        print("Starting Level 2: Functional Tests")
        
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            a2a_results = await self.a2a_messaging_test(client)
            task_results = await self.realistic_task_test(client)
            integration_results = await self.cross_agent_integration_test(client)
            
            all_results = a2a_results + task_results + integration_results
            self.results.extend(all_results)
            return all_results
    
    async def a2a_messaging_test(self, client: httpx.AsyncClient) -> List[FunctionalTestResult]:
        """Test A2A messaging between agents - 3 requests"""
        results = []
        
        for agent_name, url in self.agent_urls.items():
            start_time = time.time()
            
            try:
                a2a_message = {
                    "message_id": str(uuid.uuid4()),
                    "message_type": "health_check",
                    "sender_id": "load_tester",
                    "payload": {"test": True},
                    "timestamp": datetime.utcnow().isoformat()
                }
                
                response = await client.post(
                    f"{url}/a2a/message",
                    json=a2a_message
                )
                response_time = time.time() - start_time
                
                if response.status_code == 200:
                    response_data = response.json()
                    
                    success = response_data.get("success", False)
                    
                    results.append(FunctionalTestResult(
                        test_name="a2a_messaging",
                        agent_name=agent_name,
                        success=success,
                        response_time=response_time,
                        status_code=response.status_code,
                        task_data=a2a_message,
                        result_data=response_data
                    ))
                else:
                    results.append(FunctionalTestResult(
                        test_name="a2a_messaging",
                        agent_name=agent_name,
                        success=False,
                        response_time=response_time,
                        status_code=response.status_code,
                        task_data=a2a_message,
                        result_data={},
                        error=f"HTTP {response.status_code}"
                    ))
                    
            except Exception as e:
                response_time = time.time() - start_time
                results.append(FunctionalTestResult(
                    test_name="a2a_messaging",
                    agent_name=agent_name,
                    success=False,
                    response_time=response_time,
                    status_code=0,
                    task_data={},
                    result_data={},
                    error=str(e)
                ))
            
            await asyncio.sleep(2)
        
        return results
    
    async def realistic_task_test(self, client: httpx.AsyncClient) -> List[FunctionalTestResult]:
        """Test realistic task execution - 6 requests"""
        results = []
        
        realistic_tasks = {
            "crewai": [
                {
                    "task_type": "research",
                    "description": "Research AI trends in enterprise software for 2025",
                    "context": {"focus": "automation", "industry": "software"}
                },
                {
                    "task_type": "analysis", 
                    "description": "Analyze market opportunities for AI agents",
                    "context": {"market": "enterprise", "scope": "productivity"}
                }
            ],
            "langraph": [
                {
                    "task_type": "decision_making",
                    "description": "Choose optimal deployment strategy for AI system",
                    "context": {
                        "options": ["cloud_first", "hybrid", "on_premise"],
                        "criteria": {"cost": "medium", "security": "high"}
                    }
                },
                {
                    "task_type": "routing",
                    "description": "Route customer requests to appropriate services",
                    "context": {
                        "input_data": {"type": "support", "priority": "medium"},
                        "routing_rules": {"support": "service_desk", "sales": "sales_team"}
                    }
                }
            ],
            "adk": [
                {
                    "task_type": "data_analysis",
                    "description": "Analyze customer satisfaction data trends",
                    "context": {
                        "data": {
                            "values": [4.2, 3.8, 4.5, 4.1, 3.9, 4.3],
                            "categories": ["product", "service", "support"]
                        },
                        "analysis_type": "descriptive"
                    }
                },
                {
                    "task_type": "data_validation",
                    "description": "Validate customer data quality",
                    "context": {
                        "data": {
                            "records": [
                                {"id": 1, "email": "user@company.com", "age": 30},
                                {"id": 2, "email": "invalid.email", "age": 25}
                            ]
                        },
                        "validation_rules": {"email_format": True, "age_range": {"min": 18, "max": 65}}
                    }
                }
            ]
        }
        
        for agent_name, url in self.agent_urls.items():
            if agent_name not in realistic_tasks:
                continue
                
            for task in realistic_tasks[agent_name]:
                start_time = time.time()
                
                try:
                    response = await client.post(f"{url}/execute", json=task)
                    response_time = time.time() - start_time
                    
                    if response.status_code == 200:
                        result_data = response.json()
                        success = result_data.get("success", False)
                        
                        results.append(FunctionalTestResult(
                            test_name="realistic_task",
                            agent_name=agent_name,
                            success=success,
                            response_time=response_time,
                            status_code=response.status_code,
                            task_data=task,
                            result_data=result_data
                        ))
                    else:
                        results.append(FunctionalTestResult(
                            test_name="realistic_task",
                            agent_name=agent_name,
                            success=False,
                            response_time=response_time,
                            status_code=response.status_code,
                            task_data=task,
                            result_data={},
                            error=f"HTTP {response.status_code}"
                        ))
                        
                except Exception as e:
                    response_time = time.time() - start_time
                    results.append(FunctionalTestResult(
                        test_name="realistic_task",
                        agent_name=agent_name,
                        success=False,
                        response_time=response_time,
                        status_code=0,
                        task_data=task,
                        result_data={},
                        error=str(e)
                    ))
                
                await asyncio.sleep(3)
        
        return results
    
    async def cross_agent_integration_test(self, client: httpx.AsyncClient) -> List[FunctionalTestResult]:
        """Test cross-agent integration - 3-6 requests"""
        results = []
        
        # Test 1: CrewAI -> LangGraph collaboration
        if "crewai" in self.agent_urls and "langraph" in self.agent_urls:
            start_time = time.time()
            
            try:
                collaboration_task = {
                    "task_type": "research",
                    "description": "Research product launch strategies",
                    "context": {"product": "AI assistant", "market": "enterprise"},
                    "collaborators": {
                        "decision_maker": self.agent_urls["langraph"]
                    }
                }
                
                response = await client.post(
                    f"{self.agent_urls['crewai']}/execute",
                    json=collaboration_task
                )
                response_time = time.time() - start_time
                
                if response.status_code == 200:
                    result_data = response.json()
                    success = result_data.get("success", False)
                    has_collaboration = "collaboration" in result_data.get("result", {})
                    
                    results.append(FunctionalTestResult(
                        test_name="cross_agent_integration",
                        agent_name="crewai_to_langraph",
                        success=success and has_collaboration,
                        response_time=response_time,
                        status_code=response.status_code,
                        task_data=collaboration_task,
                        result_data=result_data
                    ))
                else:
                    results.append(FunctionalTestResult(
                        test_name="cross_agent_integration",
                        agent_name="crewai_to_langraph",
                        success=False,
                        response_time=response_time,
                        status_code=response.status_code,
                        task_data=collaboration_task,
                        result_data={},
                        error=f"HTTP {response.status_code}"
                    ))
                    
            except Exception as e:
                response_time = time.time() - start_time
                results.append(FunctionalTestResult(
                    test_name="cross_agent_integration",
                    agent_name="crewai_to_langraph",
                    success=False,
                    response_time=response_time,
                    status_code=0,
                    task_data={},
                    result_data={},
                    error=str(e)
                ))
            
            await asyncio.sleep(3)
        
        # Test 2: LangGraph -> ADK collaboration
        if "langraph" in self.agent_urls and "adk" in self.agent_urls:
            start_time = time.time()
            
            try:
                collaboration_task = {
                    "task_type": "decision_making",
                    "description": "Decide on data processing approach",
                    "context": {
                        "options": ["batch", "stream", "hybrid"],
                        "criteria": {"speed": "high", "accuracy": "critical"}
                    },
                    "collaborators": {
                        "data_processor": self.agent_urls["adk"]
                    }
                }
                
                response = await client.post(
                    f"{self.agent_urls['langraph']}/execute",
                    json=collaboration_task
                )
                response_time = time.time() - start_time
                
                if response.status_code == 200:
                    result_data = response.json()
                    success = result_data.get("success", False)
                    has_collaboration = "collaboration" in result_data.get("result", {})
                    
                    results.append(FunctionalTestResult(
                        test_name="cross_agent_integration",
                        agent_name="langraph_to_adk",
                        success=success and has_collaboration,
                        response_time=response_time,
                        status_code=response.status_code,
                        task_data=collaboration_task,
                        result_data=result_data
                    ))
                else:
                    results.append(FunctionalTestResult(
                        test_name="cross_agent_integration",
                        agent_name="langraph_to_adk",
                        success=False,
                        response_time=response_time,
                        status_code=response.status_code,
                        task_data=collaboration_task,
                        result_data={},
                        error=f"HTTP {response.status_code}"
                    ))
                    
            except Exception as e:
                response_time = time.time() - start_time
                results.append(FunctionalTestResult(
                    test_name="cross_agent_integration",
                    agent_name="langraph_to_adk",
                    success=False,
                    response_time=response_time,
                    status_code=0,
                    task_data={},
                    result_data={},
                    error=str(e)
                ))
            
            await asyncio.sleep(3)
        
        # Test 3: ADK -> CrewAI collaboration
        if "adk" in self.agent_urls and "crewai" in self.agent_urls:
            start_time = time.time()
            
            try:
                collaboration_task = {
                    "task_type": "data_analysis",
                    "description": "Analyze sales data for insights",
                    "context": {
                        "data": {"sales": [100, 150, 120, 180, 200]},
                        "analysis_type": "trend"
                    },
                    "collaborators": {
                        "researcher": self.agent_urls["crewai"]
                    }
                }
                
                response = await client.post(
                    f"{self.agent_urls['adk']}/execute",
                    json=collaboration_task
                )
                response_time = time.time() - start_time
                
                if response.status_code == 200:
                    result_data = response.json()
                    success = result_data.get("success", False)
                    has_collaboration = "collaboration" in result_data.get("result", {})
                    
                    results.append(FunctionalTestResult(
                        test_name="cross_agent_integration",
                        agent_name="adk_to_crewai",
                        success=success and has_collaboration,
                        response_time=response_time,
                        status_code=response.status_code,
                        task_data=collaboration_task,
                        result_data=result_data
                    ))
                else:
                    results.append(FunctionalTestResult(
                        test_name="cross_agent_integration",
                        agent_name="adk_to_crewai",
                        success=False,
                        response_time=response_time,
                        status_code=response.status_code,
                        task_data=collaboration_task,
                        result_data={},
                        error=f"HTTP {response.status_code}"
                    ))
                    
            except Exception as e:
                response_time = time.time() - start_time
                results.append(FunctionalTestResult(
                    test_name="cross_agent_integration",
                    agent_name="adk_to_crewai",
                    success=False,
                    response_time=response_time,
                    status_code=0,
                    task_data={},
                    result_data={},
                    error=str(e)
                ))
        
        return results
    
    def analyze_functional_results(self, results: List[FunctionalTestResult]) -> Dict[str, Any]:
        """Analyze functional test results"""
        if not results:
            return {"error": "No functional test results"}
        
        total_tests = len(results)
        successful_tests = len([r for r in results if r.success])
        
        by_test_type = {}
        for result in results:
            if result.test_name not in by_test_type:
                by_test_type[result.test_name] = {"total": 0, "success": 0, "avg_time": 0}
            by_test_type[result.test_name]["total"] += 1
            if result.success:
                by_test_type[result.test_name]["success"] += 1
        
        for test_name, stats in by_test_type.items():
            test_results = [r for r in results if r.test_name == test_name]
            response_times = [r.response_time for r in test_results if r.success]
            stats["avg_time"] = sum(response_times) / len(response_times) if response_times else 0
        
        a2a_tests = [r for r in results if r.test_name == "a2a_messaging"]
        integration_tests = [r for r in results if r.test_name == "cross_agent_integration"]
        realistic_tests = [r for r in results if r.test_name == "realistic_task"]
        
        return {
            "total_tests": total_tests,
            "successful_tests": successful_tests,
            "success_rate": (successful_tests / total_tests * 100) if total_tests > 0 else 0,
            "by_test_type": by_test_type,
            "a2a_communication": {
                "total": len(a2a_tests),
                "successful": len([r for r in a2a_tests if r.success]),
                "success_rate": (len([r for r in a2a_tests if r.success]) / len(a2a_tests) * 100) if a2a_tests else 0
            },
            "cross_agent_integration": {
                "total": len(integration_tests),
                "successful": len([r for r in integration_tests if r.success]),
                "success_rate": (len([r for r in integration_tests if r.success]) / len(integration_tests) * 100) if integration_tests else 0
            },
            "realistic_tasks": {
                "total": len(realistic_tests),
                "successful": len([r for r in realistic_tests if r.success]),
                "success_rate": (len([r for r in realistic_tests if r.success]) / len(realistic_tests) * 100) if realistic_tests else 0
            }
        }


async def run_functional_tests(agent_urls: Dict[str, str]) -> Dict[str, Any]:
    """Main function to run functional tests"""
    tester = FunctionalTester(agent_urls)
    
    start_time = time.time()
    results = await tester.run_all_functional_tests()
    total_time = time.time() - start_time
    
    analysis = tester.analyze_functional_results(results)
    
    return {
        "test_type": "functional_tests",
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
                "task_data": r.task_data,
                "result_data": r.result_data
            } for r in results
        ],
        "analysis": analysis
    }