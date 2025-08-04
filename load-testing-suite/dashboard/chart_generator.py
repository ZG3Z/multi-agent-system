# dashboard/chart_generator.py - Based on dashboard_old with enhancements
"""
Chart data generation for dashboard visualizations - Enhanced from dashboard_old
"""

from typing import Dict, List
import json

class ChartGenerator:
    
    def generate_agent_comparison_data(self, agent_stats: Dict) -> Dict:
        """Generate data for Agent Performance Comparison Chart"""
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