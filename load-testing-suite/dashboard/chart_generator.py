# dashboard/chart_generator.py
"""
Chart generation for dashboard visualizations
"""

from typing import Dict, List, Any
import json

class ChartGenerator:
    
    @staticmethod
    def generate_agent_performance_chart(agent_stats: Dict) -> str:
        """Generate agent performance comparison chart (bar + line)"""
        agent_names = list(agent_stats.keys())
        success_rates = [agent_stats[agent]["success_rate"] for agent in agent_names]
        avg_response_times = [agent_stats[agent]["avg_response_time"] * 1000 for agent in agent_names]  # Convert to ms
        
        return f"""
        <canvas id="agentPerformanceChart" width="400" height="300"></canvas>
        <script>
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
                        text: 'Agent Performance Overview'
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
        </script>
        """
    
    @staticmethod
    def generate_test_duration_chart(duration_stats: Dict) -> str:
        """Generate test duration analysis chart"""
        test_types = list(duration_stats.keys())
        avg_durations = [duration_stats[test]["avg_duration"] for test in test_types]
        
        return f"""
        <canvas id="testDurationChart" width="400" height="300"></canvas>
        <script>
        const durationCtx = document.getElementById('testDurationChart').getContext('2d');
        new Chart(durationCtx, {{
            type: 'bar',
            data: {{
                labels: {json.dumps(test_types)},
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
                        text: 'Test Duration Analysis'
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
        </script>
        """
    
    @staticmethod
    def generate_a2a_metrics_chart(a2a_stats: Dict) -> str:
        """Generate A2A communication metrics chart"""
        message_types = list(a2a_stats["message_types"].keys())
        success_rates = [
            (a2a_stats["message_types"][msg]["success"] / max(a2a_stats["message_types"][msg]["count"], 1)) * 100
            for msg in message_types
        ]
        
        return f"""
        <canvas id="a2aMetricsChart" width="400" height="300"></canvas>
        <script>
        const a2aCtx = document.getElementById('a2aMetricsChart').getContext('2d');
        new Chart(a2aCtx, {{
            type: 'doughnut',
            data: {{
                labels: {json.dumps(message_types)},
                datasets: [{{
                    label: 'A2A Success Rate (%)',
                    data: {json.dumps(success_rates)},
                    backgroundColor: [
                        'rgba(75, 192, 192, 0.8)',
                        'rgba(54, 162, 235, 0.8)',
                        'rgba(255, 206, 86, 0.8)',
                        'rgba(255, 99, 132, 0.8)'
                    ],
                    borderColor: [
                        'rgba(75, 192, 192, 1)',
                        'rgba(54, 162, 235, 1)',
                        'rgba(255, 206, 86, 1)',
                        'rgba(255, 99, 132, 1)'
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
                        text: 'A2A Communication Success Rate'
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
        </script>
        """
    
    @staticmethod
    def generate_collaboration_flow_chart(collaboration_chains: List[Dict]) -> str:
        """Generate collaboration flow visualization"""
        if not collaboration_chains:
            return '<p class="text-muted">No collaboration data available</p>'
        
        # Prepare flow data
        flow_data = []
        for chain in collaboration_chains[-10:]:  # Last 10 flows
            flow_data.append({
                "test_id": chain["test_id"][-8:],  # Short ID
                "collaborators": len(chain["collaborators"]),
                "success": chain["success"],
                "time": round(chain["total_time"], 2)
            })
        
        return f"""
        <div class="collaboration-flows">
            <h6>Recent Collaboration Flows</h6>
            <div class="flow-items">
                {"".join([
                    f'''
                    <div class="flow-item {'success' if flow['success'] else 'failed'}">
                        <small><strong>{flow['test_id']}</strong></small><br>
                        <small>{flow['collaborators']} agents</small><br>
                        <small>{flow['time']}s total</small>
                    </div>
                    ''' for flow in flow_data
                ])}
            </div>
        </div>
        <style>
        .collaboration-flows {{ margin-top: 1rem; }}
        .flow-items {{ display: flex; flex-wrap: wrap; gap: 8px; }}
        .flow-item {{ 
            padding: 8px; 
            border-radius: 4px; 
            min-width: 80px; 
            text-align: center;
            font-size: 0.8rem;
        }}
        .flow-item.success {{ 
            background-color: rgba(40, 167, 69, 0.1); 
            border: 1px solid rgba(40, 167, 69, 0.3); 
        }}
        .flow-item.failed {{ 
            background-color: rgba(220, 53, 69, 0.1); 
            border: 1px solid rgba(220, 53, 69, 0.3); 
        }}
        </style>
        """