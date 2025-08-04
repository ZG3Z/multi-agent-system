# dashboard/data_processor.py
"""
Data processing logic for dashboard metrics
"""

import os
import json
import redis
import statistics
from datetime import datetime, timedelta
from typing import Dict, List, Optional

class DataProcessor:
    def __init__(self):
        self.redis_url = os.getenv("REDIS_URL", "redis://redis:6379")
        try:
            self.redis_client = redis.from_url(self.redis_url, decode_responses=True)
            self.redis_connected = True
        except Exception as e:
            print(f"Redis connection failed: {e}")
            self.redis_client = None
            self.redis_connected = False
    
    def get_test_results(self) -> List[Dict]:
        """Get all test results from Redis and files"""
        test_results = []
        
        # From Redis
        if self.redis_client:
            try:
                for key in self.redis_client.scan_iter("test_results:*"):
                    data = self.redis_client.get(key)
                    if data:
                        result = json.loads(data)
                        test_results.append(result)
            except Exception as e:
                print(f"Error getting Redis results: {e}")
        
        # From files as backup
        results_dir = "/app/results"
        if os.path.exists(results_dir):
            for filename in os.listdir(results_dir):
                if filename.startswith("load_test_results_") and filename.endswith(".json"):
                    try:
                        with open(os.path.join(results_dir, filename), 'r') as f:
                            result = json.load(f)
                            if not any(r.get("test_id") == result.get("test_id") for r in test_results):
                                test_results.append(result)
                    except Exception as e:
                        print(f"Error reading {filename}: {e}")
        
        return sorted(test_results, key=lambda x: x.get("timestamp", ""), reverse=True)

    def get_current_status(self) -> Dict:
        """Get current test status"""
        current_status = {"running": False, "progress": "Idle"}
        
        if self.redis_client:
            try:
                for key in self.redis_client.scan_iter("test_status:*"):
                    status_data = self.redis_client.get(key)
                    if status_data:
                        status = json.loads(status_data)
                        current_status = {
                            "running": True,
                            "progress": status.get("progress", "Unknown"),
                            "current_test": status.get("current_test", ""),
                            "requests_sent": status.get("total_requests_sent", 0)
                        }
                        break
            except Exception as e:
                print(f"Error getting status: {e}")
        
        return current_status

    def get_test_by_id(self, test_id: str) -> Optional[Dict]:
        """Get specific test by ID"""
        if self.redis_client:
            data = self.redis_client.get(f"test_results:{test_id}")
            if data:
                return json.loads(data)
        
        # Try file system
        results_file = f"/app/results/load_test_results_{test_id}.json"
        if os.path.exists(results_file):
            with open(results_file, 'r') as f:
                return json.load(f)
        
        return None

    def calculate_agent_stats(self, test_results: List[Dict]) -> Dict:
        """Calculate per-agent statistics (A1, I1-I4, J1)"""
        agent_stats = {}
        
        for test in test_results:
            for result in test.get("results", []):
                agent = result.get("agent_name", "unknown")
                
                if agent not in agent_stats:
                    agent_stats[agent] = {
                        "total_requests": 0,
                        "successful_requests": 0,
                        "response_times": [],
                        "errors": []
                    }
                
                agent_stats[agent]["total_requests"] += 1
                
                if result.get("success", False):
                    agent_stats[agent]["successful_requests"] += 1
                    if "response_time" in result:
                        agent_stats[agent]["response_times"].append(result["response_time"])
                else:
                    if result.get("error"):
                        agent_stats[agent]["errors"].append(result["error"])
        
        # Calculate summary stats
        for agent, stats in agent_stats.items():
            # I1: Success Rate
            stats["success_rate"] = (stats["successful_requests"] / stats["total_requests"] * 100) if stats["total_requests"] > 0 else 0
            
            if stats["response_times"]:
                # I2: Average Response Time
                stats["avg_response_time"] = statistics.mean(stats["response_times"])
                stats["min_response_time"] = min(stats["response_times"])
                stats["max_response_time"] = max(stats["response_times"])
                
                # J1: P95 Response Time
                sorted_times = sorted(stats["response_times"])
                if len(sorted_times) > 1:
                    p95_index = int(len(sorted_times) * 0.95)
                    stats["p95_response_time"] = sorted_times[p95_index]
                    stats["std_response_time"] = statistics.stdev(stats["response_times"])
                else:
                    stats["p95_response_time"] = stats["response_times"][0]
                    stats["std_response_time"] = 0
            else:
                stats["avg_response_time"] = 0
                stats["min_response_time"] = 0
                stats["max_response_time"] = 0
                stats["p95_response_time"] = 0
                stats["std_response_time"] = 0
            
            # I4: Error Count
            stats["error_count"] = len(stats["errors"])
        
        return agent_stats

    def calculate_basic_metrics(self, test_results: List[Dict]) -> Dict:
        """Calculate basic dashboard metrics (I1-I4)"""
        if not test_results:
            return {
                "total_tests": 0,
                "total_requests": 0,
                "overall_success_rate": 0,
                "total_errors": 0
            }
        
        total_requests = 0
        successful_requests = 0
        total_errors = 0
        
        for test in test_results:
            for result in test.get("results", []):
                total_requests += 1
                if result.get("success", False):
                    successful_requests += 1
                else:
                    total_errors += 1
        
        return {
            "total_tests": len(test_results),
            "total_requests": total_requests,
            "overall_success_rate": (successful_requests / total_requests * 100) if total_requests > 0 else 0,
            "total_errors": total_errors
        }

    def calculate_p95_metrics(self, test_results: List[Dict]) -> Dict:
        """Calculate P95 response time metrics (J1)"""
        all_response_times = []
        
        for test in test_results:
            for result in test.get("results", []):
                if result.get("success") and "response_time" in result:
                    all_response_times.append(result["response_time"])
        
        if not all_response_times:
            return {"p95_response_time": 0, "p99_response_time": 0}
        
        sorted_times = sorted(all_response_times)
        p95_index = int(len(sorted_times) * 0.95)
        p99_index = int(len(sorted_times) * 0.99)
        
        return {
            "p95_response_time": sorted_times[p95_index] if p95_index < len(sorted_times) else sorted_times[-1],
            "p99_response_time": sorted_times[p99_index] if p99_index < len(sorted_times) else sorted_times[-1]
        }

    def calculate_test_duration_analysis(self, test_results: List[Dict]) -> Dict:
        """Calculate test duration analysis (B3)"""
        test_durations = {}
        
        for test in test_results:
            test_name = test.get("test_name", "unknown")
            if test_name not in test_durations:
                test_durations[test_name] = []
            
            # Estimate test duration from timestamp and results
            if test.get("results"):
                timestamps = []
                for result in test.get("results", []):
                    if result.get("timestamp"):
                        try:
                            ts = datetime.fromisoformat(result.get("timestamp").replace("Z", "+00:00"))
                            timestamps.append(ts)
                        except:
                            continue
                
                if len(timestamps) > 1:
                    duration = (max(timestamps) - min(timestamps)).total_seconds()
                    test_durations[test_name].append(duration)
        
        # Calculate stats for each test type
        duration_stats = {}
        for test_name, durations in test_durations.items():
            if durations:
                duration_stats[test_name] = {
                    "avg_duration": statistics.mean(durations),
                    "min_duration": min(durations),
                    "max_duration": max(durations),
                    "count": len(durations)
                }
        
        return duration_stats

    def calculate_a2a_metrics(self, test_results: List[Dict]) -> Dict:
        """Calculate A2A communication metrics (K1, K2)"""
        a2a_requests = []
        a2a_successful = 0
        
        for test in test_results:
            for result in test.get("results", []):
                test_name = result.get("test_name", "")
                if "a2a" in test_name.lower() or "communication" in test_name.lower():
                    a2a_requests.append(result)
                    if result.get("success", False):
                        a2a_successful += 1
        
        if not a2a_requests:
            return {
                "a2a_total_requests": 0,
                "a2a_success_rate": 0,
                "a2a_avg_latency": 0,
                "a2a_communication_latency": 0
            }
        
        # K1: Inter-agent Communication Latency
        a2a_response_times = [r.get("response_time", 0) for r in a2a_requests if r.get("success") and "response_time" in r]
        avg_latency = statistics.mean(a2a_response_times) if a2a_response_times else 0
        
        return {
            "a2a_total_requests": len(a2a_requests),
            "a2a_success_rate": (a2a_successful / len(a2a_requests) * 100) if a2a_requests else 0,  # K2
            "a2a_avg_latency": avg_latency,  # K1
            "a2a_communication_latency": avg_latency  # K1 alias
        }