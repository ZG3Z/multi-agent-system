# minimal_load_testing.py
"""
Minimal Load Testing Suite for Cloud Run Agents
Designed for free tier limits - max 30-50 API calls total
"""

import asyncio
import httpx
import time
import json
import statistics
from datetime import datetime
from typing import Dict, List, Any
from dataclasses import dataclass, asdict
from pathlib import Path

@dataclass
class TestResult:
    test_name: str
    agent_name: str
    status_code: int
    response_time: float
    success: bool
    error: str = ""
    timestamp: str = ""
    
    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now().isoformat()

class MinimalLoadTester:
    def __init__(self, agent_urls: Dict[str, str]):
        """
        Initialize with agent URLs from Cloud Run
        
        Args:
            agent_urls: {"crewai": "https://crewai-agent-xyz.run.app", ...}
        """
        self.agent_urls = agent_urls
        self.results: List[TestResult] = []
        self.client = httpx.AsyncClient(timeout=60.0)
        
    async def close(self):
        await self.client.aclose()
    
    async def health_check_test(self) -> List[TestResult]:
        """Test 1: Basic health checks (3 requests)"""
        print("Running health check test...")
        results = []
        
        for agent_name, url in self.agent_urls.items():
            start_time = time.time()
            try:
                response = await self.client.get(f"{url}/health")
                response_time = time.time() - start_time
                
                results.append(TestResult(
                    test_name="health_check",
                    agent_name=agent_name,
                    status_code=response.status_code,
                    response_time=response_time,
                    success=response.status_code == 200
                ))
                
                if response.status_code == 200:
                    data = response.json()
                    print(f"  {agent_name}: {data.get('status', 'unknown')} ({response_time:.2f}s)")
                else:
                    print(f"  {agent_name}: HTTP {response.status_code} ({response_time:.2f}s)")
                    
            except Exception as e:
                response_time = time.time() - start_time
                results.append(TestResult(
                    test_name="health_check",
                    agent_name=agent_name,
                    status_code=0,
                    response_time=response_time,
                    success=False,
                    error=str(e)
                ))
                print(f"  {agent_name}: {str(e)} ({response_time:.2f}s)")
            
            # Small delay to avoid rate limits
            await asyncio.sleep(1)
        
        return results
    
    async def capabilities_test(self) -> List[TestResult]:
        """Test 2: Check capabilities (3 requests)"""
        print("Running capabilities test...")
        results = []
        
        for agent_name, url in self.agent_urls.items():
            start_time = time.time()
            try:
                response = await self.client.get(f"{url}/capabilities")
                response_time = time.time() - start_time
                
                results.append(TestResult(
                    test_name="capabilities",
                    agent_name=agent_name,
                    status_code=response.status_code,
                    response_time=response_time,
                    success=response.status_code == 200
                ))
                
                if response.status_code == 200:
                    capabilities = response.json()
                    print(f"  {agent_name}: {len(capabilities)} capabilities ({response_time:.2f}s)")
                else:
                    print(f"  {agent_name}: HTTP {response.status_code} ({response_time:.2f}s)")
                    
            except Exception as e:
                response_time = time.time() - start_time
                results.append(TestResult(
                    test_name="capabilities",
                    agent_name=agent_name,
                    status_code=0,
                    response_time=response_time,
                    success=False,
                    error=str(e)
                ))
                print(f"  {agent_name}: {str(e)} ({response_time:.2f}s)")
            
            await asyncio.sleep(1)
        
        return results
    
    async def basic_task_test(self) -> List[TestResult]:
        """Test 3: Basic task execution (3 requests, will likely fail with fake API keys)"""
        print("Running basic task test...")
        results = []
        
        tasks = {
            "crewai": {
                "task_type": "research",
                "description": "Quick test research",
                "context": {"test": True}
            },
            "langraph": {
                "task_type": "decision_making", 
                "description": "Quick test decision",
                "context": {"options": ["A", "B"], "criteria": {"test": "value"}}
            },
            "adk": {
                "task_type": "data_transformation",
                "description": "Quick test transformation",
                "context": {"data": {"test": [1, 2, 3]}, "target_format": "json"}
            }
        }
        
        for agent_name, url in self.agent_urls.items():
            start_time = time.time()
            try:
                task_data = tasks.get(agent_name, tasks["crewai"])
                response = await self.client.post(f"{url}/execute", json=task_data)
                response_time = time.time() - start_time
                
                results.append(TestResult(
                    test_name="basic_task",
                    agent_name=agent_name,
                    status_code=response.status_code,
                    response_time=response_time,
                    success=response.status_code == 200
                ))
                
                if response.status_code == 200:
                    result_data = response.json()
                    success = result_data.get('success', False)
                    print(f"  {agent_name}: Task executed={success} ({response_time:.2f}s)")
                else:
                    print(f"  {agent_name}: HTTP {response.status_code} ({response_time:.2f}s)")
                    
            except Exception as e:
                response_time = time.time() - start_time
                results.append(TestResult(
                    test_name="basic_task",
                    agent_name=agent_name,
                    status_code=0,
                    response_time=response_time,
                    success=False,
                    error=str(e)
                ))
                print(f"  {agent_name}: {str(e)} ({response_time:.2f}s)")
            
            await asyncio.sleep(2)  # Longer delay for task execution
        
        return results
    
    async def a2a_communication_test(self) -> List[TestResult]:
        """Test 4: A2A Communication via /a2a/message endpoint (3 requests)"""
        print("Running A2A communication test...")
        results = []
        
        # Simple A2A health check message
        a2a_message = {
            "message_type": "health_check",
            "sender_id": "test-client",
            "payload": {"test": True}
        }
        
        for agent_name, url in self.agent_urls.items():
            start_time = time.time()
            try:
                response = await self.client.post(f"{url}/a2a/message", json=a2a_message)
                response_time = time.time() - start_time
                
                results.append(TestResult(
                    test_name="a2a_communication",
                    agent_name=agent_name,
                    status_code=response.status_code,
                    response_time=response_time,
                    success=response.status_code == 200
                ))
                
                if response.status_code == 200:
                    result_data = response.json()
                    success = result_data.get('success', False)
                    print(f"  {agent_name}: A2A response={success} ({response_time:.2f}s)")
                else:
                    print(f"  {agent_name}: HTTP {response.status_code} ({response_time:.2f}s)")
                    
            except Exception as e:
                response_time = time.time() - start_time
                results.append(TestResult(
                    test_name="a2a_communication",
                    agent_name=agent_name,
                    status_code=0,
                    response_time=response_time,
                    success=False,
                    error=str(e)
                ))
                print(f"  {agent_name}: {str(e)} ({response_time:.2f}s)")
            
            await asyncio.sleep(1)
        
        return results
    
    async def latency_test(self, num_requests: int = 3) -> List[TestResult]:
        """Test 5: Response time consistency (9 requests total - 3 per agent)"""
        print(f"Running latency test ({num_requests} requests per agent)...")
        results = []
        
        for agent_name, url in self.agent_urls.items():
            print(f"  Testing {agent_name} latency...")
            
            for i in range(num_requests):
                start_time = time.time()
                try:
                    response = await self.client.get(f"{url}/health")
                    response_time = time.time() - start_time
                    
                    results.append(TestResult(
                        test_name=f"latency_test_{i+1}",
                        agent_name=agent_name,
                        status_code=response.status_code,
                        response_time=response_time,
                        success=response.status_code == 200
                    ))
                    
                    print(f"    Request {i+1}: {response_time:.3f}s")
                    
                except Exception as e:
                    response_time = time.time() - start_time
                    results.append(TestResult(
                        test_name=f"latency_test_{i+1}",
                        agent_name=agent_name,
                        status_code=0,
                        response_time=response_time,
                        success=False,
                        error=str(e)
                    ))
                    print(f"    Request {i+1}: ERROR - {str(e)}")
                
                await asyncio.sleep(1)  # 1 second between requests
        
        return results
    
    def analyze_results(self, results: List[TestResult]) -> Dict[str, Any]:
        """Analyze test results and generate summary statistics"""
        if not results:
            return {"error": "No results to analyze"}
        
        # Group results by test type
        test_groups = {}
        for result in results:
            test_name = result.test_name
            if test_name not in test_groups:
                test_groups[test_name] = []
            test_groups[test_name].append(result)
        
        # Calculate statistics for each test group
        analysis = {}
        
        for test_name, test_results in test_groups.items():
            successful_results = [r for r in test_results if r.success]
            
            if successful_results:
                response_times = [r.response_time for r in successful_results]
                analysis[test_name] = {
                    "total_requests": len(test_results),
                    "successful_requests": len(successful_results),
                    "success_rate": len(successful_results) / len(test_results) * 100,
                    "response_time_stats": {
                        "min": min(response_times),
                        "max": max(response_times),
                        "avg": statistics.mean(response_times),
                        "median": statistics.median(response_times),
                    }
                }
                
                if len(response_times) > 1:
                    analysis[test_name]["response_time_stats"]["std_dev"] = statistics.stdev(response_times)
            else:
                analysis[test_name] = {
                    "total_requests": len(test_results),
                    "successful_requests": 0,
                    "success_rate": 0,
                    "errors": [r.error for r in test_results if r.error]
                }
        
        # Overall statistics
        total_requests = len(results)
        successful_requests = len([r for r in results if r.success])
        
        analysis["overall"] = {
            "total_requests": total_requests,
            "successful_requests": successful_requests,
            "overall_success_rate": successful_requests / total_requests * 100 if total_requests > 0 else 0,
            "test_duration": max([r.timestamp for r in results]) if results else "N/A"
        }
        
        return analysis
    
    def print_analysis(self, analysis: Dict[str, Any]):
        """Print analysis in human-readable format"""
        print("\n" + "="*60)
        print("LOAD TEST ANALYSIS RESULTS")
        print("="*60)
        
        # Overall stats
        overall = analysis.get("overall", {})
        print(f"Total Requests: {overall.get('total_requests', 0)}")
        print(f"Successful Requests: {overall.get('successful_requests', 0)}")
        print(f"Overall Success Rate: {overall.get('overall_success_rate', 0):.1f}%")
        print()
        
        # Individual test results
        for test_name, stats in analysis.items():
            if test_name == "overall":
                continue
                
            print(f"Test: {test_name.replace('_', ' ').title()}")
            print(f"  Requests: {stats.get('total_requests', 0)}")
            print(f"  Success Rate: {stats.get('success_rate', 0):.1f}%")
            
            if "response_time_stats" in stats:
                rt_stats = stats["response_time_stats"]
                print(f"  Response Time (avg): {rt_stats.get('avg', 0):.3f}s")
                print(f"  Response Time (min/max): {rt_stats.get('min', 0):.3f}s / {rt_stats.get('max', 0):.3f}s")
                
            if "errors" in stats and stats["errors"]:
                print(f"  Errors: {stats['errors'][:3]}")  # Show first 3 errors
            print()
    
    def save_results(self, results: List[TestResult], filename: str = None):
        """Save results to JSON file"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"load_test_results_{timestamp}.json"
        
        # Convert dataclasses to dict
        results_dict = [asdict(result) for result in results]
        
        with open(filename, 'w') as f:
            json.dump({
                "test_run_timestamp": datetime.now().isoformat(),
                "total_requests": len(results),
                "agent_urls": self.agent_urls,
                "results": results_dict
            }, f, indent=2)
        
        print(f"Results saved to: {filename}")
    
    async def collaboration_test(self) -> List[TestResult]:
        """Test 5: Agent Collaboration Test - Real A2A Workflow"""
        print("Running agent collaboration test...")
        results = []
        
        # Test full collaboration chain: Research -> Decision -> Data Processing
        collaboration_scenarios = [
            {
                "name": "research_to_decision",
                "primary_agent": "crewai",
                "task": {
                    "task_type": "research",
                    "description": "Research best practices for load testing",
                    "context": {"focus": "performance metrics"},
                    "collaborators": {
                        "decision_maker": self.agent_urls.get("langraph", "")
                    }
                }
            },
            {
                "name": "decision_to_processing",
                "primary_agent": "langraph",
                "task": {
                    "task_type": "decision_making",
                    "description": "Choose optimal data processing strategy",
                    "context": {
                        "options": ["batch", "stream", "hybrid"],
                        "criteria": {"performance": "high", "cost": "low"}
                    },
                    "collaborators": {
                        "data_processor": self.agent_urls.get("adk", "")
                    }
                }
            },
            {
                "name": "full_pipeline",
                "primary_agent": "crewai",
                "task": {
                    "task_type": "research",
                    "description": "Complete analysis pipeline test",
                    "context": {"complexity": "high"},
                    "collaborators": {
                        "decision_maker": self.agent_urls.get("langraph", ""),
                        "data_processor": self.agent_urls.get("adk", "")
                    }
                }
            }
        ]
        
        for scenario in collaboration_scenarios:
            agent_name = scenario["primary_agent"]
            scenario_name = scenario["name"]
            
            if agent_name not in self.agent_urls:
                print(f"  Skipping {scenario_name}: {agent_name} agent not available")
                continue
                
            url = self.agent_urls[agent_name]
            task_data = scenario["task"]
            
            start_time = time.time()
            try:
                print(f"  Testing {scenario_name} with {agent_name} agent...")
                response = await self.client.post(f"{url}/execute", json=task_data)
                response_time = time.time() - start_time
                
                results.append(TestResult(
                    test_name=f"collaboration_{scenario_name}",
                    agent_name=agent_name,
                    status_code=response.status_code,
                    response_time=response_time,
                    success=response.status_code == 200
                ))
                
                if response.status_code == 200:
                    result_data = response.json()
                    success = result_data.get('success', False)
                    
                    # Check if collaboration actually happened
                    collaboration_data = result_data.get('result', {}).get('collaboration', {})
                    collaborators_used = len(collaboration_data) if collaboration_data else 0
                    
                    print(f"    {scenario_name}: Task success={success}, Collaborators used={collaborators_used} ({response_time:.2f}s)")
                    
                    if collaboration_data:
                        for collaborator, collab_result in collaboration_data.items():
                            collab_success = collab_result.get('task_result', {}).get('success', False)
                            print(f"    -> {collaborator}: {collab_success}")
                else:
                    print(f"    {scenario_name}: HTTP {response.status_code} ({response_time:.2f}s)")
                    
            except Exception as e:
                response_time = time.time() - start_time
                results.append(TestResult(
                    test_name=f"collaboration_{scenario_name}",
                    agent_name=agent_name,
                    status_code=0,
                    response_time=response_time,
                    success=False,
                    error=str(e)
                ))
                print(f"    {scenario_name}: {str(e)} ({response_time:.2f}s)")
            
            await asyncio.sleep(3)  # Longer delay for collaboration tests
        
        return results

    async def run_all_tests(self) -> List[TestResult]:
        """Run all test scenarios"""
        print("Starting minimal load testing suite...")
        print(f"Testing agents: {list(self.agent_urls.keys())}")
        print(f"Estimated total requests: ~30 (including collaboration)")
        print()
        
        all_results = []
        
        try:
            # Test 1: Health checks (3 requests)
            health_results = await self.health_check_test()
            all_results.extend(health_results)
            await asyncio.sleep(2)
            
            # Test 2: Capabilities (3 requests)
            cap_results = await self.capabilities_test()
            all_results.extend(cap_results)
            await asyncio.sleep(2)
            
            # Test 3: A2A Communication (3 requests)
            a2a_results = await self.a2a_communication_test()
            all_results.extend(a2a_results)
            await asyncio.sleep(3)
            
            # Test 4: Collaboration test (3-9 requests depending on scenarios)
            collaboration_results = await self.collaboration_test()
            all_results.extend(collaboration_results)
            await asyncio.sleep(3)
            
            # Test 5: Latency test (9 requests)
            latency_results = await self.latency_test(num_requests=3)
            all_results.extend(latency_results)
            await asyncio.sleep(3)
            
            # Test 6: Basic task execution (3 requests) - may fail with fake API keys
            task_results = await self.basic_task_test()
            all_results.extend(task_results)
            
        except KeyboardInterrupt:
            print("Testing interrupted by user")
        except Exception as e:
            print(f"Testing failed: {e}")
        
        self.results = all_results
        return all_results


async def main():
    """Main testing function"""
    
    # Configure your Cloud Run URLs here
    agent_urls = {
        "crewai": "https://crewai-agent-REPLACE-run.app",
        "langraph": "https://langraph-agent-REPLACE-run.app", 
        "adk": "https://adk-agent-REPLACE-run.app"
    }
    
    # Replace with your actual Cloud Run URLs
    print("Please update agent_urls with your actual Cloud Run URLs")
    return
    
    tester = MinimalLoadTester(agent_urls)
    
    try:
        # Run all tests
        results = await tester.run_all_tests()
        
        # Analyze results
        analysis = tester.analyze_results(results)
        tester.print_analysis(analysis)
        
        # Save results
        tester.save_results(results)
        
        print(f"\nCompleted {len(results)} total requests")
        
    finally:
        await tester.close()


if __name__ == "__main__":
    asyncio.run(main())