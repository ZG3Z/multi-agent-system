# dashboard/dashboard_app.py
"""
Complete Load Test Dashboard Application
Features: Agent Performance Chart, Test Duration Analysis, Test Details Modal,
Basic & Advanced Metrics, A2A Communication Analysis, Collaboration Flows
"""

import os
import json
import redis
import uvicorn
import statistics
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse

app = FastAPI(title="Load Test Dashboard", version="3.0.0")

# Redis connection
REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379")
try:
    redis_client = redis.from_url(REDIS_URL, decode_responses=True)
    redis_client.ping()
    redis_connected = True
except Exception as e:
    print(f"Redis connection failed: {e}")
    redis_client = None
    redis_connected = False

def get_test_results() -> List[Dict]:
    """Get all test results from Redis and files"""
    test_results = []
    
    # From Redis
    if redis_connected and redis_client:
        try:
            for key in redis_client.scan_iter("test_results:*"):
                data = redis_client.get(key)
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

def get_current_test_status() -> Dict:
    """Get current test status"""
    current_status = {"running": False, "progress": "Idle"}
    
    if redis_connected and redis_client:
        try:
            for key in redis_client.scan_iter("test_status:*"):
                status_data = redis_client.get(key)
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

def get_test_duration_analysis(test_results: List[Dict]) -> Dict:
    """Analyze test durations by type"""
    duration_stats = {}
    
    for test in test_results:
        test_name = test.get("test_name", "unknown")
        execution_time = test.get("analysis", {}).get("overall", {}).get("execution_time", 0)
        
        if test_name not in duration_stats:
            duration_stats[test_name] = []
        
        if execution_time and execution_time > 0:
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

@app.get("/", response_class=HTMLResponse)
async def dashboard_home():
    """Professional dashboard with selected metrics and charts"""
    
    # Get data
    test_results = get_test_results()
    current_status = get_current_test_status()
    
    # Calculate metrics
    agent_stats = calculate_agent_stats(test_results)
    duration_stats = get_test_duration_analysis(test_results)
    a2a_metrics = get_a2a_metrics(test_results)
    collaboration_chains = get_collaboration_chains(test_results)
    
    # Calculate overall metrics
    total_requests = sum(stats['total_requests'] for stats in agent_stats.values())
    total_successful = sum(stats['successful_requests'] for stats in agent_stats.values())
    overall_success_rate = (total_successful / total_requests * 100) if total_requests > 0 else 0
    
    # Get P95 response time across all agents
    all_response_times = []
    for stats in agent_stats.values():
        all_response_times.extend(stats.get('response_times', []))
    
    p95_response_time = 0
    if all_response_times:
        sorted_times = sorted(all_response_times)
        p95_index = int(len(sorted_times) * 0.95)
        p95_response_time = sorted_times[p95_index] if sorted_times else 0
    
    # Generate test results table
    tests_html = ""
    for test in test_results[:12]:
        success_rate = test.get("analysis", {}).get("overall", {}).get("overall_success_rate", 0)
        color = "success" if success_rate >= 90 else "warning" if success_rate >= 70 else "danger"
        
        total_test_requests = test.get("total_requests", 0)
        timestamp = test.get("timestamp", "")[:19].replace("T", " ")
        
        # Calculate average response time for this test
        avg_response_time = 0
        response_times = []
        for result in test.get("results", []):
            if result.get("success") and "response_time" in result:
                response_times.append(result["response_time"])
        
        if response_times:
            avg_response_time = sum(response_times) / len(response_times)
        
        tests_html += f"""
        <tr>
            <td><code class="test-id-link" onclick="showTestDetails('{test.get('test_id', '')}')" title="Click for details">{test.get('test_id', 'unknown')}</code></td>
            <td>{test.get('test_name', 'Unknown')}</td>
            <td>{timestamp}</td>
            <td>{total_test_requests}</td>
            <td><span class="text-{color}">{success_rate:.1f}%</span></td>
            <td>{avg_response_time:.3f}s</td>
        </tr>
        """
    
    if not tests_html:
        tests_html = '''
        <tr><td colspan="6" class="text-center">
            <div class="alert alert-info">
                <h6>No test data available</h6>
                <p>Start a test to see metrics and charts</p>
                <small>Use: <code>make test-health</code> or API endpoint</small>
            </div>
        </td></tr>
        '''
    
    # Generate agent cards
    agent_cards = ""
    agent_colors = {"crewai": "primary", "langraph": "info", "adk": "success"}
    
    for agent, stats in agent_stats.items():
        color = agent_colors.get(agent, "secondary")
        
        agent_cards += f"""
        <div class="col-md-4 mb-3">
            <div class="card border-{color}">
                <div class="card-header bg-{color} text-white">
                    <h6 class="mb-0">{agent.title()} Agent</h6>
                </div>
                <div class="card-body">
                    <div class="row mb-2">
                        <div class="col-6">
                            <small class="text-muted">Success Rate</small><br>
                            <strong class="text-{color}">{stats['success_rate']:.1f}%</strong>
                        </div>
                        <div class="col-6">
                            <small class="text-muted">Total Requests</small><br>
                            <strong>{stats['total_requests']}</strong>
                        </div>
                    </div>
                    <div class="row mb-2">
                        <div class="col-6">
                            <small class="text-muted">Avg Response</small><br>
                            <strong>{stats['avg_response_time']:.3f}s</strong>
                        </div>
                        <div class="col-6">
                            <small class="text-muted">P95 Response</small><br>
                            <strong>{stats['p95_response_time']:.3f}s</strong>
                        </div>
                    </div>
                    <div class="progress" style="height: 6px;">
                        <div class="progress-bar bg-{color}" role="progressbar" 
                             style="width: {stats['success_rate']}%"></div>
                    </div>
                    {f'<small class="text-danger mt-1">Errors: {len(stats["errors"])}</small>' if stats["errors"] else ''}
                </div>
            </div>
        </div>
        """
    
    if not agent_cards:
        agent_cards = '<div class="col-12"><p class="text-muted">No agent data available</p></div>'
    
    # Prepare chart data
    agent_names = list(agent_stats.keys())
    success_rates = [agent_stats[agent]["success_rate"] for agent in agent_names]
    avg_response_times = [agent_stats[agent]["avg_response_time"] * 1000 for agent in agent_names]  # Convert to ms
    
    # Test duration chart data
    duration_types = list(duration_stats.keys())
    avg_durations = [duration_stats[test]["avg_duration"] for test in duration_types]
    
    # A2A metrics chart data
    a2a_message_types = list(a2a_metrics["message_types"].keys())
    a2a_success_rates = [
        (a2a_metrics["message_types"][msg]["success"] / max(a2a_metrics["message_types"][msg]["count"], 1)) * 100
        for msg in a2a_message_types
    ]
    
    # Collaboration flows visualization
    collaboration_flow_html = ""
    if collaboration_chains:
        for chain in collaboration_chains[-8:]:  # Last 8 flows
            status_class = "success" if chain["success"] else "danger"
            collaboration_flow_html += f"""
            <div class="col-md-3 mb-2">
                <div class="card border-{status_class}">
                    <div class="card-body p-2">
                        <small><strong>{chain['test_id'][-8:]}</strong></small><br>
                        <small>{len(chain['collaborators'])} agents</small><br>
                        <small>{chain['total_time']:.2f}s total</small>
                    </div>
                </div>
            </div>
            """
    else:
        collaboration_flow_html = '<div class="col-12"><p class="text-muted">No collaboration data available</p></div>'
    
    return f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Load Test Dashboard</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
        <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
        <meta http-equiv="refresh" content="30">
        <style>
            .metric-card {{ transition: transform 0.2s; border: none; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
            .metric-card:hover {{ transform: translateY(-2px); }}
            .chart-container {{ height: 350px; position: relative; }}
            .test-id-link {{ cursor: pointer; color: #0d6efd; }}
            .test-id-link:hover {{ text-decoration: underline; }}
            .status-running {{ background: linear-gradient(45deg, #28a745, #20c997); color: white; padding: 4px 8px; border-radius: 12px; }}
            .status-idle {{ background: linear-gradient(45deg, #6c757d, #adb5bd); color: white; padding: 4px 8px; border-radius: 12px; }}
            .navbar-brand {{ font-weight: 600; }}
            .refresh-counter {{ font-size: 0.8rem; color: #6c757d; }}
        </style>
    </head>
    <body class="bg-light">
        <nav class="navbar navbar-dark bg-dark shadow">
            <div class="container-fluid">
                <span class="navbar-brand">Load Test Dashboard</span>
                <div class="d-flex align-items-center">
                    <span class="{'status-running' if current_status['running'] else 'status-idle'} me-2">
                        {'TESTING' if current_status['running'] else 'IDLE'}
                    </span>
                    <span class="refresh-counter">Auto-refresh: 30s</span>
                </div>
            </div>
        </nav>
        
        <div class="container-fluid mt-4">
            <!-- Overall Metrics Row -->
            <div class="row mb-4">
                <div class="col-md-3">
                    <div class="card metric-card text-center">
                        <div class="card-body">
                            <h5 class="card-title">Total Tests</h5>
                            <h3 class="text-primary">{len(test_results)}</h3>
                            <small class="text-muted">All time</small>
                        </div>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="card metric-card text-center">
                        <div class="card-body">
                            <h5 class="card-title">Total Requests</h5>
                            <h3 class="text-info">{total_requests}</h3>
                            <small class="text-muted">All agents</small>
                        </div>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="card metric-card text-center">
                        <div class="card-body">
                            <h5 class="card-title">Overall Success</h5>
                            <h3 class="{'text-success' if overall_success_rate >= 90 else 'text-warning' if overall_success_rate >= 70 else 'text-danger'}">{overall_success_rate:.1f}%</h3>
                            <small class="text-muted">Success rate</small>
                        </div>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="card metric-card text-center">
                        <div class="card-body">
                            <h5 class="card-title">P95 Response</h5>
                            <h3 class="text-warning">{p95_response_time:.3f}s</h3>
                            <small class="text-muted">95th percentile</small>
                        </div>
                    </div>
                </div>
            </div>
            
            <!-- A2A Communication Metrics -->
            {f'''
            <div class="row mb-4">
                <div class="col-md-3">
                    <div class="card metric-card text-center">
                        <div class="card-body">
                            <h5 class="card-title">A2A Tests</h5>
                            <h3 class="text-info">{a2a_metrics["total_a2a_tests"]}</h3>
                            <small class="text-muted">Communication tests</small>
                        </div>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="card metric-card text-center">
                        <div class="card-body">
                            <h5 class="card-title">A2A Success</h5>
                            <h3 class="{'text-success' if a2a_metrics['a2a_success_rate'] >= 90 else 'text-warning' if a2a_metrics['a2a_success_rate'] >= 70 else 'text-danger'}">{a2a_metrics["a2a_success_rate"]:.1f}%</h3>
                            <small class="text-muted">Inter-agent success</small>
                        </div>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="card metric-card text-center">
                        <div class="card-body">
                            <h5 class="card-title">A2A Latency</h5>
                            <h3 class="text-primary">{a2a_metrics["avg_a2a_latency"]:.3f}s</h3>
                            <small class="text-muted">Avg communication time</small>
                        </div>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="card metric-card text-center">
                        <div class="card-body">
                            <h5 class="card-title">Collaborations</h5>
                            <h3 class="text-success">{len(collaboration_chains)}</h3>
                            <small class="text-muted">Multi-agent flows</small>
                        </div>
                    </div>
                </div>
            </div>
            ''' if a2a_metrics["total_a2a_tests"] > 0 else ''}
            
            <!-- Charts Row -->
            <div class="row mb-4">
                <div class="col-md-6">
                    <div class="card">
                        <div class="card-header">
                            <h5>Agent Performance Overview</h5>
                        </div>
                        <div class="card-body">
                            <div class="chart-container">
                                <canvas id="agentPerformanceChart"></canvas>
                            </div>
                        </div>
                    </div>
                </div>
                <div class="col-md-6">
                    <div class="card">
                        <div class="card-header">
                            <h5>Test Duration Analysis</h5>
                        </div>
                        <div class="card-body">
                            <div class="chart-container">
                                <canvas id="testDurationChart"></canvas>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            
            {f'''
            <!-- A2A Charts Row -->
            <div class="row mb-4">
                <div class="col-md-6">
                    <div class="card">
                        <div class="card-header">
                            <h5>A2A Communication Success</h5>
                        </div>
                        <div class="card-body">
                            <div class="chart-container">
                                <canvas id="a2aMetricsChart"></canvas>
                            </div>
                        </div>
                    </div>
                </div>
                <div class="col-md-6">
                    <div class="card">
                        <div class="card-header">
                            <h5>Recent Collaboration Flows</h5>
                        </div>
                        <div class="card-body">
                            <div class="row">
                                {collaboration_flow_html}
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            ''' if a2a_metrics["total_a2a_tests"] > 0 else ''}
            
            <!-- Agent Details Cards -->
            <div class="row mb-4">
                <div class="col-12">
                    <h4>Agent Performance Details</h4>
                </div>
                {agent_cards}
            </div>
            
            <!-- Test Results Table -->
            <div class="row">
                <div class="col-12">
                    <div class="card">
                        <div class="card-header">
                            <h5>Recent Test Results</h5>
                        </div>
                        <div class="card-body">
                            <div class="table-responsive">
                                <table class="table table-striped table-hover">
                                    <thead>
                                        <tr>
                                            <th>Test ID</th>
                                            <th>Name</th>
                                            <th>Timestamp</th>
                                            <th>Requests</th>
                                            <th>Success Rate</th>
                                            <th>Avg Response</th>
                                        </tr>
                                    </thead>
                                    <tbody>
                                        {tests_html}
                                    </tbody>
                                </table>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        
        <!-- Test Details Modal -->
        <div class="modal fade" id="testDetailsModal" tabindex="-1">
            <div class="modal-dialog modal-lg">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title">Test Details</h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                    </div>
                    <div class="modal-body" id="testDetailsContent">
                        Loading...
                    </div>
                </div>
            </div>
        </div>
        
        <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
        <script>
            // Chart.js Configuration
            Chart.defaults.font.size = 12;
            Chart.defaults.plugins.legend.position = 'bottom';
            
            // Agent Performance Chart
            {f'''
            const agentCtx = document.getElementById('agentPerformanceChart').getContext('2d');
            new Chart(agentCtx, {{
                type: 'bar',
                data: {{
                    labels: {json.dumps(agent_names)},
                    datasets: [{{
                        label: 'Success Rate (%)',
                        data: {json.dumps(success_rates)},
                        backgroundColor: 'rgba(75, 192, 192, 0.6)',
                        borderColor: 'rgba(75, 192, 192, 1)',
                        borderWidth: 1,
                        yAxisID: 'y'
                    }}, {{
                        label: 'Response Time (ms)',
                        data: {json.dumps(avg_response_times)},
                        type: 'line',
                        borderColor: 'rgba(255, 99, 132, 1)',
                        backgroundColor: 'rgba(255, 99, 132, 0.2)',
                        borderWidth: 2,
                        yAxisID: 'y1'
                    }}]
                }},
                options: {{
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {{
                        title: {{
                            display: true,
                            text: 'Success Rate vs Response Time'
                        }}
                    }},
                    scales: {{
                        y: {{
                            type: 'linear',
                            display: true,
                            position: 'left',
                            max: 100,
                            title: {{
                                display: true,
                                text: 'Success Rate (%)'
                            }}
                        }},
                        y1: {{
                            type: 'linear',
                            display: true,
                            position: 'right',
                            title: {{
                                display: true,
                                text: 'Response Time (ms)'
                            }},
                            grid: {{
                                drawOnChartArea: false,
                            }}
                        }}
                    }}
                }}
            }});
            ''' if agent_names else ''}
            
            // Test Duration Chart
            {f'''
            const durationCtx = document.getElementById('testDurationChart').getContext('2d');
            new Chart(durationCtx, {{
                type: 'bar',
                data: {{
                    labels: {json.dumps(duration_types)},
                    datasets: [{{
                        label: 'Average Duration (seconds)',
                        data: {json.dumps(avg_durations)},
                        backgroundColor: [
                            'rgba(255, 99, 132, 0.6)',
                            'rgba(54, 162, 235, 0.6)',
                            'rgba(255, 206, 86, 0.6)',
                            'rgba(75, 192, 192, 0.6)',
                            'rgba(153, 102, 255, 0.6)'
                        ],
                        borderColor: [
                            'rgba(255, 99, 132, 1)',
                            'rgba(54, 162, 235, 1)',
                            'rgba(255, 206, 86, 1)',
                            'rgba(75, 192, 192, 1)',
                            'rgba(153, 102, 255, 1)'
                        ],
                        borderWidth: 1
                    }}]
                }},
                options: {{
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {{
                        title: {{
                            display: true,
                            text: 'Average Test Duration by Type'
                        }}
                    }},
                    scales: {{
                        y: {{
                            beginAtZero: true,
                            title: {{
                                display: true,
                                text: 'Duration (seconds)'
                            }}
                        }}
                    }}
                }}
            }});
            ''' if duration_types else ''}
            
            // A2A Metrics Chart
            {f'''
            const a2aCtx = document.getElementById('a2aMetricsChart').getContext('2d');
            new Chart(a2aCtx, {{
                type: 'doughnut',
                data: {{
                    labels: {json.dumps(a2a_message_types)},
                    datasets: [{{
                        label: 'A2A Success Rate (%)',
                        data: {json.dumps(a2a_success_rates)},
                        backgroundColor: [
                            'rgba(75, 192, 192, 0.8)',
                            'rgba(54, 162, 235, 0.8)',
                            'rgba(255, 206, 86, 0.8)',
                            'rgba(255, 99, 132, 0.8)',
                            'rgba(153, 102, 255, 0.8)'
                        ],
                        borderColor: [
                            'rgba(75, 192, 192, 1)',
                            'rgba(54, 162, 235, 1)',
                            'rgba(255, 206, 86, 1)',
                            'rgba(255, 99, 132, 1)',
                            'rgba(153, 102, 255, 1)'
                        ],
                        borderWidth: 2
                    }}]
                }},
                options: {{
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {{
                        title: {{
                            display: true,
                            text: 'Inter-Agent Communication Success'
                        }},
                        tooltip: {{
                            callbacks: {{
                                label: function(context) {{
                                    return context.label + ': ' + context.formattedValue + '%';
                                }}
                            }}
                        }}
                    }}
                }}
            }});
            ''' if a2a_message_types else ''}
            
            // Test Details Modal Function
            function showTestDetails(testId) {{
                fetch(`http://localhost:8080/test/results/${{testId}}`)
                .then(response => response.json())
                .then(data => {{
                    const content = `
                        <div class="row">
                            <div class="col-md-6">
                                <h6>Test Information</h6>
                                <ul class="list-unstyled">
                                    <li><strong>ID:</strong> ${{data.test_id}}</li>
                                    <li><strong>Name:</strong> ${{data.test_name}}</li>
                                    <li><strong>Timestamp:</strong> ${{data.timestamp}}</li>
                                    <li><strong>Total Requests:</strong> ${{data.total_requests}}</li>
                                    <li><strong>Success Rate:</strong> ${{data.analysis?.overall?.overall_success_rate?.toFixed(1) || 0}}%</li>
                                </ul>
                            </div>
                            <div class="col-md-6">
                                <h6>Performance Metrics</h6>
                                <ul class="list-unstyled">
                                    <li><strong>Successful:</strong> ${{data.analysis?.overall?.successful_requests || 0}}</li>
                                    <li><strong>Failed:</strong> ${{(data.analysis?.overall?.total_requests || 0) - (data.analysis?.overall?.successful_requests || 0)}}</li>
                                    <li><strong>Execution Time:</strong> ${{data.analysis?.overall?.execution_time?.toFixed(2) || 0}}s</li>
                                </ul>
                            </div>
                        </div>
                        <hr>
                        <h6>Agent Results</h6>
                        <div class="table-responsive" style="max-height: 300px; overflow-y: auto;">
                            <table class="table table-sm">
                                <thead>
                                    <tr>
                                        <th>Agent</th>
                                        <th>Test Type</th>
                                        <th>Success</th>
                                        <th>Response Time</th>
                                        <th>Error</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    ${{data.results?.map(result => `
                                        <tr class="${{result.success ? 'table-success' : 'table-danger'}}">
                                            <td>${{result.agent_name}}</td>
                                            <td>${{result.test_name}}</td>
                                            <td>${{result.success ? '✓' : '✗'}}</td>
                                            <td>${{result.response_time ? result.response_time.toFixed(3) + 's' : 'N/A'}}</td>
                                            <td>${{result.error ? result.error.substring(0, 50) + '...' : ''}}</td>
                                        </tr>
                                    `).join('') || '<tr><td colspan="5">No results data</td></tr>'}}
                                </tbody>
                            </table>
                        </div>
                        <hr>
                        <h6>Configuration</h6>
                        <pre class="bg-light p-2 rounded" style="font-size: 0.8rem;"><code>${{JSON.stringify(data.config, null, 2)}}</code></pre>
                    `;
                    document.getElementById('testDetailsContent').innerHTML = content;
                    new bootstrap.Modal(document.getElementById('testDetailsModal')).show();
                }})
                .catch(error => {{
                    console.error('Error:', error);
                    document.getElementById('testDetailsContent').innerHTML = `
                        <div class="alert alert-danger">
                            <h6>Error Loading Test Details</h6>
                            <p>Could not load details for test ${{testId}}</p>
                            <p><strong>Error:</strong> ${{error}}</p>
                            <p>Make sure the load tester API is running on localhost:8080</p>
                        </div>
                    `;
                    new bootstrap.Modal(document.getElementById('testDetailsModal')).show();
                }});
            }}
            
            // Auto-refresh countdown
            let refreshCountdown = 30;
            const refreshElement = document.querySelector('.refresh-counter');
            
            setInterval(() => {{
                refreshCountdown--;
                refreshElement.textContent = `Auto-refresh: ${{refreshCountdown}}s`;
                if (refreshCountdown <= 0) {{
                    refreshCountdown = 30;
                }}
            }}, 1000);
            
            // Console info
            console.log('Load Test Dashboard loaded');
            console.log('Redis connected:', {redis_connected});
            console.log('Total tests:', {len(test_results)});
            console.log('Agent stats:', {json.dumps({agent: {'total': stats['total_requests'], 'success_rate': round(stats['success_rate'], 1)} for agent, stats in agent_stats.items()})});
        </script>
    </body>
    </html>
    """

@app.get("/api/test/{test_id}")
async def get_test_details(test_id: str):
    """API endpoint to get specific test details"""
    # Try Redis first
    if redis_connected and redis_client:
        try:
            data = redis_client.get(f"test_results:{test_id}")
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
    
    raise HTTPException(status_code=404, detail="Test not found")

@app.get("/api/stats")
async def get_dashboard_stats():
    """API endpoint for dashboard statistics"""
    test_results = get_test_results()
    agent_stats = calculate_agent_stats(test_results)
    a2a_metrics = get_a2a_metrics(test_results)
    
    return {
        "total_tests": len(test_results),
        "total_requests": sum(stats['total_requests'] for stats in agent_stats.values()),
        "overall_success_rate": (sum(stats['successful_requests'] for stats in agent_stats.values()) / max(sum(stats['total_requests'] for stats in agent_stats.values()), 1)) * 100,
        "redis_connected": redis_connected,
        "agent_stats": agent_stats,
        "a2a_metrics": a2a_metrics
    }

if __name__ == "__main__":
    print("Load Test Dashboard started")
    print(f"Redis: {'Connected' if redis_connected else 'Failed'}")
    print(f"Dashboard URL: http://localhost:8081")
    uvicorn.run(app, host="0.0.0.0", port=8081)