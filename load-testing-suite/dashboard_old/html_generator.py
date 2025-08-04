# dashboard/html_generator.py
"""
HTML generation for dashboard UI components
"""

from typing import Dict, List
from datetime import datetime
import statistics

class HTMLGenerator:
    
    def generate_dashboard_html(self, **kwargs) -> str:
        """Generate complete dashboard HTML"""
        
        test_results = kwargs.get("test_results", [])
        current_status = kwargs.get("current_status", {})
        agent_stats = kwargs.get("agent_stats", {})
        basic_metrics = kwargs.get("basic_metrics", {})
        p95_metrics = kwargs.get("p95_metrics", {})
        a2a_metrics = kwargs.get("a2a_metrics", {})
        agent_comparison_data = kwargs.get("agent_comparison_data", {})
        test_duration_data = kwargs.get("test_duration_data", {})
        
        # Generate components
        status_cards = self._generate_status_cards(current_status, basic_metrics, p95_metrics, a2a_metrics)
        agent_cards = self._generate_agent_cards(agent_stats)
        charts_section = self._generate_charts_section(agent_comparison_data, test_duration_data)
        test_results_table = self._generate_test_results_table(test_results)
        
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
                .metric-card {{ transition: transform 0.2s; }}
                .metric-card:hover {{ transform: translateY(-2px); }}
                .chart-container {{ height: 300px; position: relative; }}
                .bg-running {{ background: linear-gradient(45deg, #28a745, #20c997); }}
                .bg-idle {{ background: linear-gradient(45deg, #6c757d, #adb5bd); }}
                .status-badge {{ padding: 8px 12px; border-radius: 20px; }}
            </style>
        </head>
        <body>
            <nav class="navbar navbar-dark bg-dark">
                <div class="container">
                    <span class="navbar-brand">Load Test Dashboard</span>
                    <span class="badge {'bg-success' if current_status.get('running') else 'bg-secondary'}">
                        {'RUNNING' if current_status.get('running') else 'IDLE'}
                    </span>
                </div>
            </nav>
            
            <div class="container-fluid mt-4">
                <!-- Status Cards (I1-I4, J1, K1-K2) -->
                {status_cards}
                
                <!-- Charts -->
                {charts_section}
                
                <!-- Agent Performance Cards -->
                <div class="row mb-4">
                    <div class="col-12">
                        <h4>Agent Performance Details</h4>
                    </div>
                    {agent_cards}
                </div>
                
                <!-- Test Results Table -->
                {test_results_table}
            </div>
            
            <!-- Test Details Modal (F1) -->
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
            {self._generate_javascript(agent_comparison_data, test_duration_data)}
        </body>
        </html>
        """
    
    def _generate_status_cards(self, current_status: Dict, basic_metrics: Dict, p95_metrics: Dict, a2a_metrics: Dict) -> str:
        """Generate status metric cards"""
        return f"""
        <div class="row mb-4">
            <div class="col-md-2">
                <div class="card metric-card">
                    <div class="card-body text-center">
                        <h6 class="card-title">System Status</h6>
                        <span class="status-badge {'bg-running text-white' if current_status.get('running') else 'bg-idle text-white'}">
                            {current_status.get('progress', 'Idle')}
                        </span>
                    </div>
                </div>
            </div>
            <div class="col-md-2">
                <div class="card metric-card">
                    <div class="card-body text-center">
                        <h6 class="card-title">Total Tests</h6>
                        <h4 class="text-primary">{basic_metrics.get('total_tests', 0)}</h4>
                        <small class="text-muted">All time</small>
                    </div>
                </div>
            </div>
            <div class="col-md-2">
                <div class="card metric-card">
                    <div class="card-body text-center">
                        <h6 class="card-title">Total Requests</h6>
                        <h4 class="text-info">{basic_metrics.get('total_requests', 0)}</h4>
                        <small class="text-muted">Volume</small>
                    </div>
                </div>
            </div>
            <div class="col-md-2">
                <div class="card metric-card">
                    <div class="card-body text-center">
                        <h6 class="card-title">Success Rate</h6>
                        <h4 class="{'text-success' if basic_metrics.get('overall_success_rate', 0) >= 90 else 'text-warning' if basic_metrics.get('overall_success_rate', 0) >= 70 else 'text-danger'}">{basic_metrics.get('overall_success_rate', 0):.1f}%</h4>
                        <small class="text-muted">Overall</small>
                    </div>
                </div>
            </div>
            <div class="col-md-2">
                <div class="card metric-card">
                    <div class="card-body text-center">
                        <h6 class="card-title">P95 Response</h6>
                        <h4 class="text-warning">{p95_metrics.get('p95_response_time', 0):.3f}s</h4>
                        <small class="text-muted">95th Percentile</small>
                    </div>
                </div>
            </div>
            <div class="col-md-2">
                <div class="card metric-card">
                    <div class="card-body text-center">
                        <h6 class="card-title">A2A Latency</h6>
                        <h4 class="text-info">{a2a_metrics.get('a2a_avg_latency', 0):.3f}s</h4>
                        <small class="text-muted">Inter-agent</small>
                    </div>
                </div>
            </div>
        </div>
        
        <div class="row mb-4">
            <div class="col-md-3">
                <div class="card metric-card">
                    <div class="card-body text-center">
                        <h6 class="card-title">Total Errors</h6>
                        <h4 class="text-danger">{basic_metrics.get('total_errors', 0)}</h4>
                        <small class="text-muted">Error Count</small>
                    </div>
                </div>
            </div>
            <div class="col-md-3">
                <div class="card metric-card">
                    <div class="card-body text-center">
                        <h6 class="card-title">A2A Requests</h6>
                        <h4 class="text-secondary">{a2a_metrics.get('a2a_total_requests', 0)}</h4>
                        <small class="text-muted">Count</small>
                    </div>
                </div>
            </div>
            <div class="col-md-3">
                <div class="card metric-card">
                    <div class="card-body text-center">
                        <h6 class="card-title">A2A Success Rate</h6>
                        <h4 class="{'text-success' if a2a_metrics.get('a2a_success_rate', 0) >= 90 else 'text-warning' if a2a_metrics.get('a2a_success_rate', 0) >= 70 else 'text-danger'}">{a2a_metrics.get('a2a_success_rate', 0):.1f}%</h4>
                        <small class="text-muted">A2A Quality</small>
                    </div>
                </div>
            </div>
            <div class="col-md-3">
                <div class="card metric-card">
                    <div class="card-body text-center">
                        <h6 class="card-title">Last Update</h6>
                        <h6 class="text-muted">{datetime.now().strftime('%H:%M:%S')}</h6>
                        <small class="text-muted">Auto-refresh 30s</small>
                    </div>
                </div>
            </div>
        </div>
        """
    
    def _generate_agent_cards(self, agent_stats: Dict) -> str:
        """Generate agent performance cards"""
        if not agent_stats:
            return '<div class="col-12"><p class="text-muted">No agent statistics available yet.</p></div>'
        
        cards_html = ""
        for agent, stats in agent_stats.items():
            success_color = "success" if stats["success_rate"] >= 90 else "warning" if stats["success_rate"] >= 70 else "danger"
            
            cards_html += f"""
            <div class="col-md-4 mb-3">
                <div class="card">
                    <div class="card-header bg-{success_color} text-white">
                        <h6 class="mb-0">{agent.title()} Agent</h6>
                    </div>
                    <div class="card-body">
                        <div class="row">
                            <div class="col-6">
                                <small class="text-muted">Success Rate</small><br>
                                <strong>{stats['success_rate']:.1f}%</strong>
                            </div>
                            <div class="col-6">
                                <small class="text-muted">Total Requests</small><br>
                                <strong>{stats['total_requests']}</strong>
                            </div>
                        </div>
                        <hr>
                        <div class="row">
                            <div class="col-6">
                                <small class="text-muted">Avg Response</small><br>
                                <strong>{stats['avg_response_time']:.3f}s</strong>
                            </div>
                            <div class="col-6">
                                <small class="text-muted">P95 Response</small><br>
                                <strong>{stats['p95_response_time']:.3f}s</strong>
                            </div>
                        </div>
                        <div class="row mt-2">
                            <div class="col-6">
                                <small class="text-muted">Min/Max</small><br>
                                <strong>{stats['min_response_time']:.3f}s / {stats['max_response_time']:.3f}s</strong>
                            </div>
                            <div class="col-6">
                                <small class="text-muted">Errors</small><br>
                                <strong class="text-danger">{stats['error_count']}</strong>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            """
        
        return cards_html
    
    def _generate_charts_section(self, agent_comparison_data: Dict, test_duration_data: Dict) -> str:
        """Generate charts section"""
        return f"""
        <div class="row mb-4">
            <div class="col-md-6">
                <div class="card">
                    <div class="card-header">
                        <h5>Agent Performance Comparison</h5>
                        <small class="text-muted">Success Rate vs Response Time</small>
                    </div>
                    <div class="card-body">
                        <div class="chart-container">
                            <canvas id="agentComparisonChart"></canvas>
                        </div>
                    </div>
                </div>
            </div>
            <div class="col-md-6">
                <div class="card">
                    <div class="card-header">
                        <h5>Test Duration Analysis</h5>
                        <small class="text-muted">Average duration by test type</small>
                    </div>
                    <div class="card-body">
                        <div class="chart-container">
                            <canvas id="testDurationChart"></canvas>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        """
    
    def _generate_test_results_table(self, test_results: List[Dict]) -> str:
        """Generate test results table"""
        if not test_results:
            table_rows = """
            <tr><td colspan="7" class="text-center">
                <div class="alert alert-info">
                    <h6>No tests yet!</h6>
                    <p>Use Quick Actions above to run your first test</p>
                </div>
            </td></tr>
            """
        else:
            table_rows = ""
            for test in test_results[:15]:
                success_rate = test.get("analysis", {}).get("overall", {}).get("overall_success_rate", 0)
                color = "success" if success_rate >= 90 else "warning" if success_rate >= 70 else "danger"
                
                total_requests = test.get("total_requests", 0)
                timestamp = test.get("timestamp", "")[:19].replace("T", " ")
                
                # Calculate average response time
                avg_response_time = 0
                response_times = []
                for result in test.get("results", []):
                    if result.get("success") and "response_time" in result:
                        response_times.append(result["response_time"])
                
                if response_times:
                    avg_response_time = statistics.mean(response_times)
                
                table_rows += f"""
                <tr>
                    <td><code>{test.get('test_id', 'unknown')}</code></td>
                    <td>{test.get('test_name', 'Unknown')}</td>
                    <td>{timestamp}</td>
                    <td>{total_requests}</td>
                    <td><span class="text-{color}">{success_rate:.1f}%</span></td>
                    <td>{avg_response_time:.3f}s</td>
                    <td>
                        <button class="btn btn-sm btn-outline-primary" onclick="showTestDetails('{test.get('test_id', '')}')">
                            Details
                        </button>
                    </td>
                </tr>
                """
        
        return f"""
        <div class="row">
            <div class="col-12">
                <div class="card">
                    <div class="card-header">
                        <h5>Recent Test Results</h5>
                        <small class="text-muted">Click Details for full test information</small>
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
                                        <th>Actions</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {table_rows}
                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        """
    
    def _generate_javascript(self, agent_comparison_data: Dict, test_duration_data: Dict) -> str:
        """Generate JavaScript for charts and interactions"""
        return f"""
        <script>
            // Chart.js Configuration
            Chart.defaults.font.size = 12;
            Chart.defaults.plugins.legend.position = 'bottom';
            
            // Agent Comparison Chart (A1)
            const agentCtx = document.getElementById('agentComparisonChart').getContext('2d');
            new Chart(agentCtx, {{
                type: 'bar',
                data: {{
                    labels: {agent_comparison_data.get('labels', [])},
                    datasets: [{{
                        label: 'Success Rate (%)',
                        data: {agent_comparison_data.get('success_rates', [])},
                        backgroundColor: ['rgba(75, 192, 192, 0.6)', 'rgba(54, 162, 235, 0.6)', 'rgba(255, 206, 86, 0.6)'],
                        borderColor: ['rgba(75, 192, 192, 1)', 'rgba(54, 162, 235, 1)', 'rgba(255, 206, 86, 1)'],
                        borderWidth: 1,
                        yAxisID: 'y'
                    }}, {{
                        label: 'Avg Response Time (ms)',
                        data: {agent_comparison_data.get('response_times', [])},
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
                                drawOnChartArea: false
                            }}
                        }}
                    }},
                    plugins: {{
                        legend: {{
                            position: 'bottom'
                        }}
                    }}
                }}
            }});
            
            // Test Duration Chart (B3)
            const durationCtx = document.getElementById('testDurationChart').getContext('2d');
            new Chart(durationCtx, {{
                type: 'bar',
                data: {{
                    labels: {test_duration_data.get('labels', [])},
                    datasets: [{{
                        label: 'Average Duration (s)',
                        data: {test_duration_data.get('avg_durations', [])},
                        backgroundColor: 'rgba(153, 102, 255, 0.6)',
                        borderColor: 'rgba(153, 102, 255, 1)',
                        borderWidth: 1
                    }}, {{
                        label: 'Min Duration (s)',
                        data: {test_duration_data.get('min_durations', [])},
                        backgroundColor: 'rgba(255, 159, 64, 0.6)',
                        borderColor: 'rgba(255, 159, 64, 1)', 
                        borderWidth: 1
                    }}, {{
                        label: 'Max Duration (s)',
                        data: {test_duration_data.get('max_durations', [])},
                        backgroundColor: 'rgba(255, 99, 132, 0.6)',
                        borderColor: 'rgba(255, 99, 132, 1)',
                        borderWidth: 1
                    }}]
                }},
                options: {{
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {{
                        y: {{
                            beginAtZero: true,
                            title: {{
                                display: true,
                                text: 'Duration (seconds)'
                            }}
                        }}
                    }},
                    plugins: {{
                        legend: {{
                            position: 'bottom'
                        }}
                    }}
                }}
            }});
            
            // Test Details Modal
            function showTestDetails(testId) {{
                fetch(`http://localhost:8081/api/test/${{testId}}`)
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
                                </ul>
                            </div>
                            <div class="col-md-6">
                                <h6>Metrics Summary</h6>
                                <ul class="list-unstyled">
                                    <li><strong>Success Rate:</strong> ${{data.analysis?.overall?.overall_success_rate?.toFixed(1) || 0}}%</li>
                                    <li><strong>Successful:</strong> ${{data.analysis?.overall?.successful_requests || 0}}</li>
                                    <li><strong>Errors:</strong> ${{(data.analysis?.overall?.total_requests || 0) - (data.analysis?.overall?.successful_requests || 0)}}</li>
                                </ul>
                            </div>
                        </div>
                        <hr>
                        <h6>Test Configuration</h6>
                        <pre class="bg-light p-3 rounded"><code>${{JSON.stringify(data.config, null, 2)}}</code></pre>
                        <h6>Full Analysis</h6>
                        <pre class="bg-light p-3 rounded" style="max-height: 300px; overflow-y: auto;">
                            <code>${{JSON.stringify(data.analysis, null, 2)}}</code>
                        </pre>
                    `;
                    document.getElementById('testDetailsContent').innerHTML = content;
                    new bootstrap.Modal(document.getElementById('testDetailsModal')).show();
                }})
                .catch(error => {{
                    document.getElementById('testDetailsContent').innerHTML = `
                        <div class="alert alert-danger">
                            <h6>Error Loading Test Details</h6>
                            <p>Could not load details for test ${{testId}}</p>
                            <p><strong>Error:</strong> ${{error}}</p>
                        </div>
                    `;
                    new bootstrap.Modal(document.getElementById('testDetailsModal')).show();
                }});
            }}
        </script>
        """