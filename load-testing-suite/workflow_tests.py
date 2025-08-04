"""
Workflow Tests - Level 3
Sequential agent workflows and complex scenarios
Estimated requests: 15-18 total
"""

import asyncio
import time
from typing import Dict, List, Any
from dataclasses import dataclass
from datetime import datetime


@dataclass
class WorkflowResult:
    workflow_name: str
    agent_chain: List[str]
    total_time: float
    success: bool
    steps_completed: int
    final_result: Dict[str, Any]
    error: str = ""


class WorkflowTester:
    def __init__(self, agent_urls: Dict[str, str], client):
        self.agent_urls = agent_urls
        self.client = client
        self.results = []
    
    async def run_all_workflows(self) -> List[WorkflowResult]:
        """Run all workflow tests"""
        print("Starting Level 3: Workflow Tests")
        
        workflows = [
            await self.research_decision_processing_workflow(),
            await self.data_analysis_pipeline_workflow(),
            await self.decision_routing_workflow()
        ]
        
        self.results.extend(workflows)
        return workflows
    
    async def research_decision_processing_workflow(self) -> WorkflowResult:
        """Workflow: CrewAI research -> LangGraph decision -> ADK processing"""
        workflow_name = "research_decision_processing"
        agent_chain = ["crewai", "langraph", "adk"]
        start_time = time.time()
        
        try:
            # Step 1: Research with CrewAI
            research_task = {
                "task_type": "research",
                "description": "Research AI implementation strategies for enterprise",
                "context": {"focus": "cost_effective_solutions", "timeline": "2025"}
            }
            
            response1 = await self.client.post(
                f"{self.agent_urls['crewai']}/execute",
                json=research_task,
                timeout=45
            )
            
            if response1.status_code != 200:
                raise Exception(f"Research step failed: {response1.status_code}")
            
            research_result = response1.json()
            
            # Step 2: Decision making with LangGraph
            decision_task = {
                "task_type": "decision_making",
                "description": "Choose optimal AI implementation approach",
                "context": {
                    "research_data": research_result.get("result", {}),
                    "options": ["phased_rollout", "pilot_program", "full_deployment"],
                    "criteria": {"cost": "medium", "risk": "low", "timeline": "6_months"}
                }
            }
            
            response2 = await self.client.post(
                f"{self.agent_urls['langraph']}/execute", 
                json=decision_task,
                timeout=45
            )
            
            if response2.status_code != 200:
                raise Exception(f"Decision step failed: {response2.status_code}")
            
            decision_result = response2.json()
            
            # Step 3: Data processing with ADK
            processing_task = {
                "task_type": "data_transformation",
                "description": "Transform decision data into implementation plan",
                "context": {
                    "decision_data": decision_result.get("result", {}),
                    "target_format": "implementation_plan",
                    "transformations": ["normalize_columns", "remove_nulls"]
                }
            }
            
            response3 = await self.client.post(
                f"{self.agent_urls['adk']}/execute",
                json=processing_task, 
                timeout=45
            )
            
            if response3.status_code != 200:
                raise Exception(f"Processing step failed: {response3.status_code}")
            
            processing_result = response3.json()
            
            total_time = time.time() - start_time
            
            return WorkflowResult(
                workflow_name=workflow_name,
                agent_chain=agent_chain,
                total_time=total_time,
                success=True,
                steps_completed=3,
                final_result={
                    "research": research_result.get("result", {}),
                    "decision": decision_result.get("result", {}), 
                    "processing": processing_result.get("result", {})
                }
            )
            
        except Exception as e:
            total_time = time.time() - start_time
            return WorkflowResult(
                workflow_name=workflow_name,
                agent_chain=agent_chain,
                total_time=total_time,
                success=False,
                steps_completed=0,
                final_result={},
                error=str(e)
            )
    
    async def data_analysis_pipeline_workflow(self) -> WorkflowResult:
        """Workflow: ADK validation -> CrewAI analysis -> LangGraph routing"""
        workflow_name = "data_analysis_pipeline"
        agent_chain = ["adk", "crewai", "langraph"]
        start_time = time.time()
        
        try:
            # Step 1: Data validation with ADK
            validation_task = {
                "task_type": "data_validation",
                "description": "Validate customer dataset quality",
                "context": {
                    "data": {
                        "records": [
                            {"id": 1, "email": "user@example.com", "age": 25, "score": 85},
                            {"id": 2, "email": "invalid-email", "age": 30, "score": 92},
                            {"id": 3, "email": "test@test.com", "age": -5, "score": None}
                        ]
                    },
                    "validation_rules": {"email_format": True, "age_range": {"min": 0, "max": 120}}
                }
            }
            
            response1 = await self.client.post(
                f"{self.agent_urls['adk']}/execute",
                json=validation_task,
                timeout=45
            )
            
            if response1.status_code != 200:
                raise Exception(f"Validation step failed: {response1.status_code}")
            
            validation_result = response1.json()
            
            # Step 2: Analysis with CrewAI
            analysis_task = {
                "task_type": "analysis",
                "description": "Analyze data validation results and provide insights",
                "context": {
                    "validation_results": validation_result.get("result", {}),
                    "focus": "data_quality_issues"
                }
            }
            
            response2 = await self.client.post(
                f"{self.agent_urls['crewai']}/execute",
                json=analysis_task,
                timeout=45
            )
            
            if response2.status_code != 200:
                raise Exception(f"Analysis step failed: {response2.status_code}")
            
            analysis_result = response2.json()
            
            # Step 3: Routing with LangGraph
            routing_task = {
                "task_type": "routing",
                "description": "Route analysis results to appropriate team",
                "context": {
                    "input_data": analysis_result.get("result", {}),
                    "routing_rules": {
                        "high_quality": "production_team",
                        "medium_quality": "data_cleaning_team", 
                        "low_quality": "data_collection_team"
                    }
                }
            }
            
            response3 = await self.client.post(
                f"{self.agent_urls['langraph']}/execute",
                json=routing_task,
                timeout=45
            )
            
            if response3.status_code != 200:
                raise Exception(f"Routing step failed: {response3.status_code}")
            
            routing_result = response3.json()
            
            total_time = time.time() - start_time
            
            return WorkflowResult(
                workflow_name=workflow_name,
                agent_chain=agent_chain,
                total_time=total_time,
                success=True,
                steps_completed=3,
                final_result={
                    "validation": validation_result.get("result", {}),
                    "analysis": analysis_result.get("result", {}),
                    "routing": routing_result.get("result", {})
                }
            )
            
        except Exception as e:
            total_time = time.time() - start_time
            return WorkflowResult(
                workflow_name=workflow_name,
                agent_chain=agent_chain,
                total_time=total_time,
                success=False,
                steps_completed=0,
                final_result={},
                error=str(e)
            )
    
    async def decision_routing_workflow(self) -> WorkflowResult:
        """Workflow: LangGraph decision -> route to specialist -> return"""
        workflow_name = "decision_routing"
        agent_chain = ["langraph", "dynamic", "langraph"]
        start_time = time.time()
        
        try:
            # Step 1: Initial routing decision
            routing_task = {
                "task_type": "routing",
                "description": "Route task to appropriate specialist",
                "context": {
                    "input_data": {"task_type": "data_processing", "complexity": "medium"},
                    "routing_rules": {
                        "data_processing": "adk",
                        "research": "crewai",
                        "decision": "langraph"
                    }
                }
            }
            
            response1 = await self.client.post(
                f"{self.agent_urls['langraph']}/execute",
                json=routing_task,
                timeout=45
            )
            
            if response1.status_code != 200:
                raise Exception(f"Initial routing failed: {response1.status_code}")
            
            routing_result = response1.json()
            route = routing_result.get("result", {}).get("route", "adk")
            
            # Step 2: Execute on routed agent
            if route == "adk" and "adk" in self.agent_urls:
                specialist_task = {
                    "task_type": "data_aggregation",
                    "description": "Aggregate sample data by category",
                    "context": {
                        "data": {
                            "records": [
                                {"category": "A", "value": 100},
                                {"category": "B", "value": 200},
                                {"category": "A", "value": 150}
                            ]
                        },
                        "groupby_columns": ["category"],
                        "aggregation_functions": {"value": ["sum", "mean"]}
                    }
                }
                target_url = self.agent_urls["adk"]
            else:
                specialist_task = {
                    "task_type": "research", 
                    "description": "Quick research on routing patterns",
                    "context": {"focus": "agent_routing"}
                }
                target_url = self.agent_urls["crewai"]
            
            response2 = await self.client.post(
                f"{target_url}/execute",
                json=specialist_task,
                timeout=45
            )
            
            if response2.status_code != 200:
                raise Exception(f"Specialist execution failed: {response2.status_code}")
            
            specialist_result = response2.json()
            
            # Step 3: Final decision compilation
            compilation_task = {
                "task_type": "decision_making",
                "description": "Compile workflow results and make final recommendation",
                "context": {
                    "routing_decision": routing_result.get("result", {}),
                    "specialist_output": specialist_result.get("result", {}),
                    "options": ["accept_results", "request_refinement", "escalate"],
                    "criteria": {"quality": "high", "completeness": "required"}
                }
            }
            
            response3 = await self.client.post(
                f"{self.agent_urls['langraph']}/execute",
                json=compilation_task,
                timeout=45
            )
            
            if response3.status_code != 200:
                raise Exception(f"Final compilation failed: {response3.status_code}")
            
            final_result = response3.json()
            
            total_time = time.time() - start_time
            
            return WorkflowResult(
                workflow_name=workflow_name,
                agent_chain=agent_chain,
                total_time=total_time,
                success=True,
                steps_completed=3,
                final_result={
                    "initial_routing": routing_result.get("result", {}),
                    "specialist_work": specialist_result.get("result", {}),
                    "final_decision": final_result.get("result", {})
                }
            )
            
        except Exception as e:
            total_time = time.time() - start_time
            return WorkflowResult(
                workflow_name=workflow_name,
                agent_chain=agent_chain,
                total_time=total_time,
                success=False,
                steps_completed=0,
                final_result={},
                error=str(e)
            )
    
    def analyze_workflow_results(self, results: List[WorkflowResult]) -> Dict[str, Any]:
        """Analyze workflow test results"""
        if not results:
            return {"error": "No workflow results to analyze"}
        
        total_workflows = len(results)
        successful_workflows = len([r for r in results if r.success])
        total_time = sum([r.total_time for r in results])
        avg_time = total_time / total_workflows if total_workflows > 0 else 0
        
        workflow_stats = {}
        for result in results:
            workflow_stats[result.workflow_name] = {
                "success": result.success,
                "execution_time": result.total_time,
                "steps_completed": result.steps_completed,
                "agent_chain": result.agent_chain,
                "error": result.error if not result.success else None
            }
        
        return {
            "total_workflows": total_workflows,
            "successful_workflows": successful_workflows,
            "success_rate": (successful_workflows / total_workflows * 100) if total_workflows > 0 else 0,
            "total_execution_time": total_time,
            "average_execution_time": avg_time,
            "workflow_details": workflow_stats
        }


async def run_workflow_tests(agent_urls: Dict[str, str], client) -> Dict[str, Any]:
    """Main function to run workflow tests"""
    tester = WorkflowTester(agent_urls, client)
    
    start_time = time.time()
    results = await tester.run_all_workflows()
    total_time = time.time() - start_time
    
    analysis = tester.analyze_workflow_results(results)
    analysis["test_execution_time"] = total_time
    
    return {
        "test_type": "workflow_tests",
        "timestamp": datetime.utcnow().isoformat(),
        "results": [
            {
                "workflow_name": r.workflow_name,
                "agent_chain": r.agent_chain,
                "success": r.success,
                "execution_time": r.total_time,
                "steps_completed": r.steps_completed,
                "error": r.error,
                "final_result": r.final_result
            } for r in results
        ],
        "analysis": analysis
    }