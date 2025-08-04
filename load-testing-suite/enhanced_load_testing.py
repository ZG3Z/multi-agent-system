"""
Enhanced Load Testing Suite with 3 Levels
Main orchestrator for basic, functional, and workflow tests
"""

import asyncio
import time
import os
from typing import Dict, List, Any
from datetime import datetime

# Import test modules
from basic_tests import BasicTester
from functional_tests import FunctionalTester  
from workflow_tests import WorkflowTester


class EnhancedLoadTester:
    def __init__(self, agent_urls: Dict[str, str]):
        self.agent_urls = agent_urls
        self.test_results = {}
        
    async def run_level(self, level: int) -> Dict[str, Any]:
        """Run tests for specific level"""
        start_time = time.time()
        
        if level == 1:
            print("Running Level 1: Basic Tests (9 requests)")
            tester = BasicTester(self.agent_urls)
            results = await tester.run_all_basic_tests()
            analysis = self._analyze_basic_results(results)
            
        elif level == 2:
            print("Running Level 2: Functional Tests (12-18 requests)")
            tester = FunctionalTester(self.agent_urls)
            results = await tester.run_all_functional_tests()
            analysis = self._analyze_functional_results(results)
            
        elif level == 3:
            print("Running Level 3: Workflow Tests (15-18 requests)")
            tester = WorkflowTester(self.agent_urls)
            results = await tester.run_all_workflow_tests()
            analysis = self._analyze_workflow_results(results)
            
        else:
            raise ValueError(f"Invalid test level: {level}")
        
        execution_time = time.time() - start_time
        
        return {
            "level": level,
            "timestamp": datetime.utcnow().isoformat(),
            "execution_time": execution_time,
            "results": results,
            "analysis": analysis
        }
    
    async def run_all_levels(self) -> Dict[str, Any]:
        """Run all test levels sequentially"""
        print("Starting Enhanced Load Testing Suite")
        print("="*50)
        
        all_results = {}
        total_start = time.time()
        
        for level in [1, 2, 3]:
            try:
                level_results = await self.run_level(level)
                all_results[f"level_{level}"] = level_results
                
                # Small delay between levels
                await asyncio.sleep(2)
                
            except Exception as e:
                print(f"Level {level} failed: {e}")
                all_results[f"level_{level}"] = {
                    "level": level,
                    "error": str(e),
                    "timestamp": datetime.utcnow().isoformat()
                }
        
        total_time = time.time() - total_start
        
        # Overall analysis
        overall_analysis = self._analyze_overall_results(all_results)
        
        return {
            "test_suite": "enhanced_load_testing",
            "timestamp": datetime.utcnow().isoformat(),
            "total_execution_time": total_time,
            "levels_completed": len([v for v in all_results.values() if "error" not in v]),
            "results": all_results,
            "overall_analysis": overall_analysis
        }
    
    def _analyze_basic_results(self, results: List) -> Dict[str, Any]:
        """Analyze basic test results"""
        if not results:
            return {"error": "No basic test results"}
        
        total_tests = len(results)
        successful_tests = len([r for r in results if r.success])
        avg_response_time = sum([r.response_time for r in results]) / total_tests
        
        agent_stats = {}
        for result in results:
            if result.agent_name not in agent_stats:
                agent_stats[result.agent_name] = {"total": 0, "success": 0, "avg_time": 0}
            
            agent_stats[result.agent_name]["total"] += 1
            if result.success:
                agent_stats[result.agent_name]["success"] += 1
        
        # Calculate success rates
        for agent, stats in agent_stats.items():
            stats["success_rate"] = (stats["success"] / stats["total"] * 100) if stats["total"] > 0 else 0
        
        return {
            "total_tests": total_tests,
            "successful_tests": successful_tests,
            "success_rate": (successful_tests / total_tests * 100) if total_tests > 0 else 0,
            "average_response_time": avg_response_time,
            "agent_stats": agent_stats
        }
    
    def _analyze_functional_results(self, results: List) -> Dict[str, Any]:
        """Analyze functional test results"""
        if not results:
            return {"error": "No functional test results"}
        
        total_tests = len(results)
        successful_tests = len([r for r in results if r.success])
        
        test_types = {}
        for result in results:
            if result.test_name not in test_types:
                test_types[result.test_name] = {"total": 0, "success": 0}
            
            test_types[result.test_name]["total"] += 1
            if result.success:
                test_types[result.test_name]["success"] += 1
        
        # Calculate success rates per test type
        for test_type, stats in test_types.items():
            stats["success_rate"] = (stats["success"] / stats["total"] * 100) if stats["total"] > 0 else 0
        
        return {
            "total_tests": total_tests,
            "successful_tests": successful_tests,
            "success_rate": (successful_tests / total_tests * 100) if total_tests > 0 else 0,
            "test_type_stats": test_types
        }
    
    def _analyze_workflow_results(self, results: List) -> Dict[str, Any]:
        """Analyze workflow test results"""
        if not results:
            return {"error": "No workflow test results"}
        
        total_workflows = len(results)
        successful_workflows = len([r for r in results if r.success])
        
        workflow_stats = {}
        for result in results:
            workflow_stats[result.workflow_name] = {
                "success": result.success,
                "execution_time": result.total_time,
                "steps_completed": result.steps_completed,
                "agent_chain": result.agent_chain
            }
        
        return {
            "total_workflows": total_workflows,
            "successful_workflows": successful_workflows,
            "success_rate": (successful_workflows / total_workflows * 100) if total_workflows > 0 else 0,
            "workflow_details": workflow_stats
        }
    
    def _analyze_overall_results(self, all_results: Dict) -> Dict[str, Any]:
        """Analyze overall test suite results"""
        levels_run = len(all_results)
        levels_successful = len([v for v in all_results.values() if "error" not in v])
        
        total_requests = 0
        for level_name, level_data in all_results.items():
            if "analysis" in level_data:
                total_requests += level_data["analysis"].get("total_tests", 0)
        
        return {
            "levels_run": levels_run,
            "levels_successful": levels_successful,
            "total_requests_sent": total_requests,
            "overall_success_rate": (levels_successful / levels_run * 100) if levels_run > 0 else 0
        }


# Standalone execution
async def main():
    """Main function for standalone execution"""
    agent_urls = {
        "crewai": os.getenv("CREWAI_URL", "http://localhost:8080"),
        "langraph": os.getenv("LANGRAPH_URL", "http://localhost:8082"), 
        "adk": os.getenv("ADK_URL", "http://localhost:8083")
    }
    
    # Validate URLs
    for name, url in agent_urls.items():
        if "localhost" in url:
            print(f"Warning: {name} using localhost URL: {url}")
    
    tester = EnhancedLoadTester(agent_urls)
    
    # Run specific level or all
    test_level = int(os.getenv("TEST_LEVEL", "0"))
    
    if test_level in [1, 2, 3]:
        results = await tester.run_level(test_level)
        print(f"\nLevel {test_level} Results:")
        print(f"Success Rate: {results['analysis']['success_rate']:.1f}%")
    else:
        results = await tester.run_all_levels()
        print(f"\nOverall Results:")
        print(f"Levels Completed: {results['levels_completed']}/3")
        print(f"Total Requests: {results['overall_analysis']['total_requests_sent']}")
    
    # Save results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"enhanced_test_results_{timestamp}.json"
    
    import json
    with open(f"/app/results/{filename}", "w") as f:
        json.dump(results, f, indent=2, default=str)
    
    print(f"\nResults saved to: {filename}")


if __name__ == "__main__":
    asyncio.run(main())