# dashboard/data_provider.py
"""
Data provider for dashboard - handles Redis and file system data
"""

import os
import json
import redis
from typing import Dict, List, Optional

class DataProvider:
    
    def __init__(self, redis_url: str = "redis://redis:6379"):
        self.redis_url = redis_url
        self.redis_client = None
        self.redis_connected = False
        self._connect_redis()
    
    def _connect_redis(self):
        """Connect to Redis"""
        try:
            self.redis_client = redis.from_url(self.redis_url, decode_responses=True)
            # Test connection
            self.redis_client.ping()
            self.redis_connected = True
        except Exception as e:
            print(f"Redis connection failed: {e}")
            self.redis_client = None
            self.redis_connected = False
    
    def get_test_results(self) -> List[Dict]:
        """Get all test results from Redis and files"""
        test_results = []
        
        # From Redis
        if self.redis_connected and self.redis_client:
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
                            # Avoid duplicates
                            if not any(r.get("test_id") == result.get("test_id") for r in test_results):
                                test_results.append(result)
                    except Exception as e:
                        print(f"Error reading {filename}: {e}")
        
        return sorted(test_results, key=lambda x: x.get("timestamp", ""), reverse=True)
    
    def get_current_test_status(self) -> Dict:
        """Get current test status"""
        current_status = {"running": False, "progress": "Idle"}
        
        if self.redis_connected and self.redis_client:
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
                print(f"Error getting test status: {e}")
        
        return current_status
    
    def get_test_by_id(self, test_id: str) -> Optional[Dict]:
        """Get specific test by ID"""
        # Try Redis first
        if self.redis_connected and self.redis_client:
            try:
                data = self.redis_client.get(f"test_results:{test_id}")
                if data:
                    return json.loads(data)
            except Exception as e:
                print(f"Error getting test {test_id} from Redis: {e}")
        
        # Try files
        results_file = f"/app/results/load_test_results_{test_id}.json"
        if os.path.exists(results_file):
            try:
                with open(results_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error reading {results_file}: {e}")
        
        return None
    
    def get_system_info(self) -> Dict:
        """Get system information"""
        return {
            "redis_connected": self.redis_connected,
            "redis_url": self.redis_url,
            "results_dir_exists": os.path.exists("/app/results")
        }