# dashboard/dashboard_app.py - Main FastAPI application
"""
Refactored Load Test Dashboard - Main Application
"""

import os
import uvicorn
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse
from datetime import datetime

from data_processor import DataProcessor
from chart_generator import ChartGenerator
from html_generator import HTMLGenerator

app = FastAPI(title="Refactored Load Test Dashboard", version="2.0.0")

# Initialize components
data_processor = DataProcessor()
chart_generator = ChartGenerator()
html_generator = HTMLGenerator()

@app.get("/", response_class=HTMLResponse)
async def dashboard_home():
    """Main dashboard page with selected features"""
    
    # Get all data
    test_results = data_processor.get_test_results()
    current_status = data_processor.get_current_status()
    
    # Calculate metrics
    agent_stats = data_processor.calculate_agent_stats(test_results)
    basic_metrics = data_processor.calculate_basic_metrics(test_results)
    p95_metrics = data_processor.calculate_p95_metrics(test_results)
    test_duration_analysis = data_processor.calculate_test_duration_analysis(test_results)
    a2a_metrics = data_processor.calculate_a2a_metrics(test_results)
    
    # Generate charts data
    agent_comparison_data = chart_generator.generate_agent_comparison_data(agent_stats)
    test_duration_data = chart_generator.generate_test_duration_data(test_duration_analysis)
    
    # Generate HTML
    html_content = html_generator.generate_dashboard_html(
        test_results=test_results,
        current_status=current_status,
        agent_stats=agent_stats,
        basic_metrics=basic_metrics,
        p95_metrics=p95_metrics,
        a2a_metrics=a2a_metrics,
        agent_comparison_data=agent_comparison_data,
        test_duration_data=test_duration_data
    )
    
    return html_content

@app.get("/api/tests")
async def api_tests():
    """API endpoint for test list"""
    test_results = data_processor.get_test_results()
    return {
        "tests": [
            {
                "test_id": t.get("test_id"), 
                "test_name": t.get("test_name"), 
                "timestamp": t.get("timestamp")
            } for t in test_results
        ],
        "total": len(test_results),
        "redis_connected": data_processor.redis_connected
    }

@app.get("/api/test/{test_id}")
async def api_get_test(test_id: str):
    """Get specific test details"""
    test_data = data_processor.get_test_by_id(test_id)
    if not test_data:
        raise HTTPException(status_code=404, detail="Test not found")
    return test_data

@app.get("/api/metrics")
async def api_metrics():
    """Get current metrics"""
    test_results = data_processor.get_test_results()
    return {
        "basic_metrics": data_processor.calculate_basic_metrics(test_results),
        "agent_stats": data_processor.calculate_agent_stats(test_results),
        "a2a_metrics": data_processor.calculate_a2a_metrics(test_results)
    }

if __name__ == "__main__":
    print("Refactored Dashboard started")
    print(f"Redis: {'Connected' if data_processor.redis_connected else 'Failed'}")
    uvicorn.run(app, host="0.0.0.0", port=8081)