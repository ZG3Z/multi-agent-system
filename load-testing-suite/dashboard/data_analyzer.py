# dashboard/data_analyzer.py
"""
Data analysis module for dashboard metrics
"""

import statistics
from typing import Dict, List, Any
from datetime import datetime, timedelta

class DashboardAnalyzer:
    
    @staticmethod
    def calculate_agent_stats(test_results: List[Dict]) -> Dict:
        """Calculate comprehensive per-agent statistics"""
        agent_stats = {}
        
        for test in test_results:
            for result in test.get("results", []):
                agent = result.get("agent_name", "unknown")
                
                if agent not in agent_stats:
                    agent_stats[agent] = {
                        "total_requests": 0,
                        "successful_requests": 0,
                        "response_times": [],
                        "errors": [],
                        "test_types": {}
                    }
                
                agent_stats[agent]["total_requests"] += 1
                
                # Track test types
                test_type = result.get("test_name", "unknown")
                if test_type not in agent_stats[agent]["test_types"]:
                    agent_stats[agent]["test_types"][test_type] = {"count": 0, "success": 0}
                agent_stats[agent]["test_types"][test_type]["count"] += 1
                
                if result.get("success", False):
                    agent_stats[agent]["successful_requests"] += 1
                    agent_stats[agent]["test_types"][test_type]["success"] += 1
                    if "response_time" in result:
                        agent_stats[agent]["response_times"].append(result["response_time"])
                else:
                    if result.get("error"):
                        agent_stats[agent]["errors"].append(result["error"])
        
        # Calculate summary stats
        for agent, stats in agent_stats.items():
            if stats["response_times"]:
                stats["avg_response_time"] = statistics.mean(stats["response_times"])
                stats["min_response_time"] = min(stats["response_times"])
                stats["max_response_time"] = max(stats["response_times"])
                
                # P95 percentile
                sorted_times = sorted(stats["response_times"])
                p95_index = int(len(sorted_times) * 0.95)
                stats["p95_response_time"] = sorted_times[p95_index] if sorted_times else 0
                
                if len(stats["response_times"]) > 1:
                    stats["std_response_time"] = statistics.stdev(stats["response_times"])
                else:
                    stats["std_response_time"] = 0
            else:
                stats.update({
                    "avg_response_time": 0,
                    "min_response_time": 0,
                    "max_response_time": 0,
                    "p95_response_time": 0,
                    "std_response_time": 0
                })
            
            stats["success_rate"] = (stats["successful_requests"] / stats["total_requests"] * 100) if stats["total_requests"] > 0 else 0
        
        return agent_stats
    
    @staticmethod
    def get_test_duration_analysis(test_results: List[Dict]) -> Dict:
        """Analyze test durations by type"""
        duration_stats = {}
        
        for test in test_results:
            test_name = test.get("test_name", "unknown")
            execution_time = test.get("analysis", {}).get("overall", {}).get("execution_time", 0)
            
            if test_name not in duration_stats:
                duration_stats[test_name] = []
            
            if execution_time > 0:
                duration_stats[test_name].append(execution_time)
        
        # Calculate statistics for each test type
        result = {}
        for test_type, durations in duration_stats.items():
            if durations:
                result[test_type] = {
                    "avg_duration": statistics.mean(durations),
                    "min_duration": min(durations),
                    "max_duration": max(durations),
                    "count": len(durations)
                }
        
        return result
    
    @staticmethod
    def get_a2a_metrics(test_results: List[Dict]) -> Dict:
        """Calculate A2A communication specific metrics"""
        a2a_stats = {
            "total_a2a_tests": 0,
            "successful_a2a_tests": 0,
            "a2a_response_times": [],
            "message_types": {},
            "collaboration_flows": []
        }
        
        for test in test_results:
            for result in test.get("results", []):
                test_name = result.get("test_name", "")
                
                if "a2a" in test_name or "communication" in test_name:
                    a2a_stats["total_a2a_tests"] += 1
                    
                    if result.get("success", False):
                        a2a_stats["successful_a2a_tests"] += 1
                        if "response_time" in result:
                            a2a_stats["a2a_response_times"].append(result["response_time"])
                    
                    # Track message types
                    if test_name not in a2a_stats["message_types"]:
                        a2a_stats["message_types"][test_name] = {"count": 0, "success": 0}
                    
                    a2a_stats["message_types"][test_name]["count"] += 1
                    if result.get("success", False):
                        a2a_stats["message_types"][test_name]["success"] += 1
        
        # Calculate A2A success rate
        if a2a_stats["total_a2a_tests"] > 0:
            a2a_stats["a2a_success_rate"] = (a2a_stats["successful_a2a_tests"] / a2a_stats["total_a2a_tests"]) * 100
        else:
            a2a_stats["a2a_success_rate"] = 0
        
        # Calculate A2A latency
        if a2a_stats["a2a_response_times"]:
            a2a_stats["avg_a2a_latency"] = statistics.mean(a2a_stats["a2a_response_times"])
        else:
            a2a_stats["avg_a2a_latency"] = 0
        
        return a2a_stats
    
    @staticmethod
    def get_collaboration_chains(test_results: List[Dict]) -> List[Dict]:
        """Analyze agent collaboration patterns"""
        chains = []
        
        for test in test_results:
            if test.get("config", {}).get("collaborators"):
                collaborators = test["config"]["collaborators"]
                chain = {
                    "test_id": test.get("test_id", "unknown"),
                    "initiator": "test_client",
                    "collaborators": list(collaborators.keys()),
                    "success": test.get("analysis", {}).get("overall", {}).get("overall_success_rate", 0) > 80,
                    "total_time": sum(r.get("response_time", 0) for r in test.get("results", []) if r.get("success"))
                }
                chains.append(chain)
        
        return chains