import asyncio
import time
from typing import Dict, Any, List, Callable
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from langchain_google_genai import ChatGoogleGenerativeAI
from models import TaskType, AgentCapability
from config import Config

class WorkflowState(Dict):
    """State object for LangGraph workflows"""
    pass

class LangGraphLogic:
    def __init__(self):
        try:
            if not Config.GOOGLE_API_KEY:
                raise ValueError("GOOGLE_API_KEY not found in environment variables")
            
            # Initialize LLM for LangGraph
            self.llm = ChatGoogleGenerativeAI(
                model=Config.GEMINI_MODEL,
                google_api_key=Config.GOOGLE_API_KEY,
                temperature=0.7
            )
            
            self.capabilities = self._define_capabilities()
            self.memory = MemorySaver()
            
            print(f"LangGraph agent initialized with Gemini model: {Config.GEMINI_MODEL}")
            
        except Exception as e:
            print(f"LangGraph initialization failed: {e}")
            raise
    
    def _define_capabilities(self) -> List[AgentCapability]:
        return [
            AgentCapability(
                name="decision_making",
                description="Make decisions based on input criteria",
                input_schema={
                    "type": "object",
                    "properties": {
                        "task_type": {"type": "string", "enum": ["decision_making"]},
                        "description": {"type": "string"},
                        "options": {"type": "array"},
                        "criteria": {"type": "object"}
                    },
                    "required": ["task_type", "description"]
                },
                output_schema={
                    "type": "object",
                    "properties": {
                        "decision": {"type": "string"},
                        "reasoning": {"type": "string"},
                        "confidence": {"type": "number"}
                    }
                },
                estimated_duration=120
            ),
            AgentCapability(
                name="workflow",
                description="Execute multi-step workflows with state management",
                input_schema={
                    "type": "object",
                    "properties": {
                        "task_type": {"type": "string", "enum": ["workflow"]},
                        "description": {"type": "string"},
                        "steps": {"type": "array"},
                        "initial_state": {"type": "object"}
                    },
                    "required": ["task_type", "description"]
                },
                output_schema={
                    "type": "object",
                    "properties": {
                        "final_state": {"type": "object"},
                        "execution_path": {"type": "array"},
                        "step_results": {"type": "array"}
                    }
                },
                estimated_duration=180
            ),
            AgentCapability(
                name="routing",
                description="Route requests to appropriate handlers",
                input_schema={
                    "type": "object",
                    "properties": {
                        "task_type": {"type": "string", "enum": ["routing"]},
                        "description": {"type": "string"},
                        "input_data": {"type": "object"},
                        "routing_rules": {"type": "object"}
                    },
                    "required": ["task_type", "description"]
                },
                output_schema={
                    "type": "object",
                    "properties": {
                        "route": {"type": "string"},
                        "routed_data": {"type": "object"},
                        "routing_reason": {"type": "string"}
                    }
                },
                estimated_duration=60
            ),
            AgentCapability(
                name="conditional_logic",
                description="Execute conditional logic and branching",
                input_schema={
                    "type": "object",
                    "properties": {
                        "task_type": {"type": "string", "enum": ["conditional_logic"]},
                        "description": {"type": "string"},
                        "conditions": {"type": "array"},
                        "data": {"type": "object"}
                    },
                    "required": ["task_type", "description"]
                },
                output_schema={
                    "type": "object",
                    "properties": {
                        "branch_taken": {"type": "string"},
                        "result": {"type": "object"},
                        "conditions_evaluated": {"type": "array"}
                    }
                },
                estimated_duration=90
            )
        ]
    
    async def execute_task(self, task_type: TaskType, description: str, 
                          context: Dict[str, Any] = None) -> Dict[str, Any]:
        start_time = time.time()
        
        try:
            print(f"Executing {task_type.value} task: {description[:100]}...")
            
            if task_type == TaskType.DECISION_MAKING:
                result = await self._decision_making_task(description, context)
            elif task_type == TaskType.WORKFLOW:
                result = await self._workflow_task(description, context)
            elif task_type == TaskType.ROUTING:
                result = await self._routing_task(description, context)
            elif task_type == TaskType.CONDITIONAL_LOGIC:
                result = await self._conditional_logic_task(description, context)
            else:
                raise ValueError(f"Unsupported task type: {task_type}")
            
            execution_time = time.time() - start_time
            print(f"Task completed in {execution_time:.2f}s")
            
            return {
                "success": True,
                "result": result,
                "execution_time": execution_time,
                "task_type": task_type.value
            }
            
        except Exception as e:
            execution_time = time.time() - start_time
            error_msg = str(e)
            print(f"Task failed after {execution_time:.2f}s: {error_msg}")
            return {
                "success": False,
                "error": error_msg,
                "execution_time": execution_time,
                "task_type": task_type.value,
                "result": {}
            }
    
    async def _decision_making_task(self, description: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Decision making using LangGraph"""
        
        def analyze_options(state: WorkflowState) -> WorkflowState:
            """Analyze available options"""
            options = context.get("options", []) if context else []
            criteria = context.get("criteria", {}) if context else {}
            
            prompt = f"""
            Decision Required: {description}
            
            Available Options: {options}
            Decision Criteria: {criteria}
            
            Analyze each option against the criteria and provide reasoning.
            """
            
            try:
                response = self.llm.invoke(prompt)
                analysis = response.content if hasattr(response, 'content') and response.content else "Analysis completed"
            except Exception as e:
                analysis = f"Analysis failed: {str(e)}"
            
            state["analysis"] = analysis
            state["options"] = options
            return state
        
        def make_decision(state: WorkflowState) -> WorkflowState:
            """Make the final decision"""
            
            analysis = state.get('analysis', 'No analysis available')
            prompt = f"""
            Based on the analysis: {analysis}
            
            Make a final decision and provide:
            1. The chosen option
            2. Clear reasoning
            3. Confidence level (0-1)
            
            Format as: DECISION: [choice] | REASONING: [reason] | CONFIDENCE: [0-1]
            """
            
            try:
                response = self.llm.invoke(prompt)
                content = response.content if hasattr(response, 'content') and response.content else "Decision: default"
            except Exception as e:
                content = f"Decision: default | REASONING: Error occurred: {str(e)} | CONFIDENCE: 0.1"
            
            # Parse response
            try:
                parts = content.split(" | ")
                decision = parts[0].replace("DECISION: ", "").strip()
                reasoning = parts[1].replace("REASONING: ", "").strip() if len(parts) > 1 else "No reasoning provided"
                confidence = float(parts[2].replace("CONFIDENCE: ", "").strip()) if len(parts) > 2 else 0.5
            except:
                decision = content
                reasoning = "Decision made based on analysis"
                confidence = 0.8
            
            state["decision"] = decision
            state["reasoning"] = reasoning
            state["confidence"] = confidence
            return state
        
        # Create decision workflow
        workflow = StateGraph(WorkflowState)
        workflow.add_node("analyze", analyze_options)
        workflow.add_node("decide", make_decision)
        
        workflow.set_entry_point("analyze")
        workflow.add_edge("analyze", "decide")
        workflow.add_edge("decide", END)
        
        app = workflow.compile(checkpointer=self.memory)
        
        # Execute workflow
        initial_state = {"description": description}
        try:
            loop = asyncio.get_event_loop()
            final_state = await loop.run_in_executor(
                None,
                lambda: app.invoke(initial_state, config={"configurable": {"thread_id": "decision_thread"}})
            )
            
            # Ensure final_state is not None
            if final_state is None:
                final_state = {
                    "decision": "No decision could be made",
                    "reasoning": "Workflow execution returned None",
                    "confidence": 0.1,
                    "analysis": "Analysis failed"
                }
        except Exception as e:
            final_state = {
                "decision": "Error in decision making",
                "reasoning": f"Workflow failed: {str(e)}",
                "confidence": 0.1,
                "analysis": "Analysis failed due to error"
            }
        
        return {
            "decision": final_state.get("decision", "No decision made"),
            "reasoning": final_state.get("reasoning", "No reasoning provided"),
            "confidence": final_state.get("confidence", 0.5),
            "analysis": final_state.get("analysis", "No analysis available")
        }
    
    async def _workflow_task(self, description: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Multi-step workflow execution"""
        
        steps = context.get("steps", []) if context else []
        initial_state = context.get("initial_state", {}) if context else {}
        
        def step_executor(step_name: str) -> Callable:
            """Create a step executor function"""
            def execute_step(state: WorkflowState) -> WorkflowState:
                prompt = f"""
                Workflow Step: {step_name}
                Description: {description}
                Current State: {state}
                
                Execute this step and update the state accordingly.
                Provide the updated state and any results.
                """
                
                try:
                    response = self.llm.invoke(prompt)
                    result_content = response.content if hasattr(response, 'content') and response.content else f"Step {step_name} completed"
                except Exception as e:
                    result_content = f"Step {step_name} failed: {str(e)}"
                
                # Update state with step result
                if "step_results" not in state:
                    state["step_results"] = []
                
                state["step_results"].append({
                    "step": step_name,
                    "result": result_content,
                    "timestamp": time.time()
                })
                
                # Update execution path
                if "execution_path" not in state:
                    state["execution_path"] = []
                state["execution_path"].append(step_name)
                
                return state
            
            return execute_step
        
        # Create workflow with steps
        workflow = StateGraph(WorkflowState)
        
        if steps:
            # Add nodes for each step
            for i, step in enumerate(steps):
                step_name = f"step_{i}_{step}"
                workflow.add_node(step_name, step_executor(step))
                
                if i == 0:
                    workflow.set_entry_point(step_name)
                else:
                    prev_step = f"step_{i-1}_{steps[i-1]}"
                    workflow.add_edge(prev_step, step_name)
                
                if i == len(steps) - 1:
                    workflow.add_edge(step_name, END)
        else:
            # Default single step workflow
            def default_step(state: WorkflowState) -> WorkflowState:
                prompt = f"""
                Execute workflow: {description}
                Initial State: {state}
                
                Process the workflow and provide results.
                """
                
                response = self.llm.invoke(prompt)
                state["result"] = response.content
                state["execution_path"] = ["default_step"]
                return state
            
            workflow.add_node("default", default_step)
            workflow.set_entry_point("default")
            workflow.add_edge("default", END)
        
        app = workflow.compile(checkpointer=self.memory)
        
        # Execute workflow
        workflow_state = {**initial_state, "description": description}
        try:
            loop = asyncio.get_event_loop()
            final_state = await loop.run_in_executor(
                None,
                lambda: app.invoke(workflow_state, config={"configurable": {"thread_id": "workflow_thread"}})
            )
            
            # Ensure final_state is not None
            if final_state is None:
                final_state = {
                    "execution_path": ["error"],
                    "step_results": [{"step": "error", "result": "Workflow execution failed", "timestamp": time.time()}],
                    "description": description
                }
        except Exception as e:
            final_state = {
                "execution_path": ["error"],
                "step_results": [{"step": "error", "result": f"Workflow failed: {str(e)}", "timestamp": time.time()}],
                "description": description
            }
        
        return {
            "final_state": dict(final_state),
            "execution_path": final_state.get("execution_path", []),
            "step_results": final_state.get("step_results", []),
            "workflow_description": description
        }
    
    async def _routing_task(self, description: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Route requests to appropriate handlers"""
        
        input_data = context.get("input_data", {}) if context else {}
        routing_rules = context.get("routing_rules", {}) if context else {}
        
        prompt = f"""
        Routing Decision Required: {description}
        
        Input Data: {input_data}
        Routing Rules: {routing_rules}
        
        Determine the appropriate route for this request and provide:
        1. The selected route
        2. Any data transformations needed
        3. Reasoning for the routing decision
        
        Format as: ROUTE: [route] | DATA: [transformed_data] | REASON: [reasoning]
        """
        
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(
            None,
            lambda: self.llm.invoke(prompt)
        )
        
        content = response.content
        
        # Parse response
        try:
            parts = content.split(" | ")
            route = parts[0].replace("ROUTE: ", "").strip()
            routed_data = parts[1].replace("DATA: ", "").strip()
            reasoning = parts[2].replace("REASON: ", "").strip()
        except:
            route = "default"
            routed_data = str(input_data)
            reasoning = content
        
        return {
            "route": route,
            "routed_data": routed_data,
            "routing_reason": reasoning,
            "original_data": input_data
        }
    
    async def _conditional_logic_task(self, description: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Execute conditional logic and branching"""
        
        conditions = context.get("conditions", []) if context else []
        data = context.get("data", {}) if context else {}
        
        def evaluate_condition(condition: str, data: Dict) -> bool:
            """Simple condition evaluator"""
            # This is a simplified evaluator - in production you'd want more robust logic
            try:
                # Replace data references in condition
                for key, value in data.items():
                    condition = condition.replace(f"{key}", str(value))
                
                # Evaluate simple conditions
                if ">" in condition:
                    left, right = condition.split(">")
                    return float(left.strip()) > float(right.strip())
                elif "<" in condition:
                    left, right = condition.split("<")
                    return float(left.strip()) < float(right.strip())
                elif "==" in condition:
                    left, right = condition.split("==")
                    return left.strip() == right.strip()
                
                return True
            except:
                return False
        
        # Evaluate all conditions
        evaluated_conditions = []
        for condition in conditions:
            result = evaluate_condition(condition, data)
            evaluated_conditions.append({
                "condition": condition,
                "result": result
            })
        
        # Determine branch
        branch_taken = "default"
        for eval_condition in evaluated_conditions:
            if eval_condition["result"]:
                branch_taken = f"condition_true_{eval_condition['condition']}"
                break
        
        # Execute branch logic
        prompt = f"""
        Conditional Logic Execution: {description}
        
        Data: {data}
        Conditions Evaluated: {evaluated_conditions}
        Branch Taken: {branch_taken}
        
        Execute the logic for the selected branch and provide results.
        """
        
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(
            None,
            lambda: self.llm.invoke(prompt)
        )
        
        return {
            "branch_taken": branch_taken,
            "result": response.content,
            "conditions_evaluated": evaluated_conditions,
            "input_data": data
        }
    
    def get_capabilities(self) -> List[AgentCapability]:
        return self.capabilities