# dashboard/chart_generator.py
"""
Chart data generation for dashboard visualizations
"""

from typing import Dict, List
import json

class ChartGenerator:
    
    def generate_agent_comparison_data(self, agent_stats: Dict) -> Dict:
        """Generate data for Agent Performance Comparison Chart (A1)"""
        if not agent_stats:
            return {
                "labels": [],
                "success_rates": [],
                "response_times": []
            }
        
        agent_names = list(agent_stats.keys())
        success_rates = [agent_stats[agent]["success_rate"] for agent in agent_names]
        # Convert to milliseconds for better readability
        response_times = [agent_stats[agent]["avg_response_time"] * 1000 for agent in agent_names]
        
        return {
            "labels": agent_names,
            "success_rates": success_rates,
            "response_times": response_times
        }
    
    def generate_test_duration_data(self, duration_analysis: Dict) -> Dict:
        """Generate data for Test Duration Analysis Chart (B3)"""
        if not duration_analysis:
            return {
                "labels": [],
                "avg_durations": [],
                "min_durations": [],
                "max_durations": []
            }
        
        test_names = list(duration_analysis.keys())
        avg_durations = [duration_analysis[test]["avg_duration"] for test in test_names]
        min_durations = [duration_analysis[test]["min_duration"] for test in test_names]
        max_durations = [duration_analysis[test]["max_duration"] for test in test_names]
        
        return {
            "labels": test_names,
            "avg_durations": avg_durations,
            "min_durations": min_durations,
            "max_durations": max_durations
        }
    
    def generate_chart_configs(self) -> Dict:
        """Generate Chart.js configuration templates"""
        return {
            "agent_comparison": {
                "type": "bar",
                "options": {
                    "responsive": True,
                    "maintainAspectRatio": False,
                    "scales": {
                        "y": {
                            "type": "linear",
                            "display": True,
                            "position": "left",
                            "max": 100,
                            "title": {
                                "display": True,
                                "text": "Success Rate (%)"
                            }
                        },
                        "y1": {
                            "type": "linear",
                            "display": True,
                            "position": "right",
                            "title": {
                                "display": True,
                                "text": "Response Time (ms)"
                            },
                            "grid": {
                                "drawOnChartArea": False
                            }
                        }
                    },
                    "plugins": {
                        "legend": {
                            "position": "bottom"
                        },
                        "tooltip": {
                            "mode": "index",
                            "intersect": False
                        }
                    }
                }
            },
            "test_duration": {
                "type": "bar",
                "options": {
                    "responsive": True,
                    "maintainAspectRatio": False,
                    "scales": {
                        "y": {
                            "beginAtZero": True,
                            "title": {
                                "display": True,
                                "text": "Duration (seconds)"
                            }
                        },
                        "x": {
                            "title": {
                                "display": True,
                                "text": "Test Types"
                            }
                        }
                    },
                    "plugins": {
                        "legend": {
                            "position": "bottom"
                        },
                        "tooltip": {
                            "callbacks": {
                                "label": "function(context) { return context.dataset.label + ': ' + context.raw.toFixed(2) + 's'; }"
                            }
                        }
                    }
                }
            }
        }
    
    def generate_chart_colors(self) -> Dict:
        """Generate consistent color scheme for charts"""
        return {
            "agents": {
                "crewai": {
                    "background": "rgba(75, 192, 192, 0.6)",
                    "border": "rgba(75, 192, 192, 1)"
                },
                "langraph": {
                    "background": "rgba(54, 162, 235, 0.6)",
                    "border": "rgba(54, 162, 235, 1)"
                },
                "adk": {
                    "background": "rgba(255, 206, 86, 0.6)",
                    "border": "rgba(255, 206, 86, 1)"
                }
            },
            "metrics": {
                "success": {
                    "background": "rgba(40, 167, 69, 0.6)",
                    "border": "rgba(40, 167, 69, 1)"
                },
                "response_time": {
                    "background": "rgba(255, 99, 132, 0.6)", 
                    "border": "rgba(255, 99, 132, 1)"
                },
                "error": {
                    "background": "rgba(220, 53, 69, 0.6)",
                    "border": "rgba(220, 53, 69, 1)"
                }
            }
        }