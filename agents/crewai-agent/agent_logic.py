import asyncio
import time
import google.generativeai as genai
from typing import Dict, Any, List
from models import TaskType, AgentCapability
from config import Config

class CrewAILogic:
    def __init__(self):
        try:
            if not Config.GOOGLE_API_KEY:
                raise ValueError("GOOGLE_API_KEY not found in environment variables")
            
            # Configure Gemini
            genai.configure(api_key=Config.GOOGLE_API_KEY)
            
            # Initialize model
            self.model = genai.GenerativeModel(Config.GEMINI_MODEL)
            self.capabilities = self._define_capabilities()
            
            print(f"Agent initialized with Gemini model: {Config.GEMINI_MODEL}")
            
        except Exception as e:
            print(f"Agent initialization failed: {e}")
            raise
    
    def _define_capabilities(self) -> List[AgentCapability]:
        return [
            AgentCapability(
                name="research",
                description="Research topics and gather information",
                input_schema={
                    "type": "object",
                    "properties": {
                        "task_type": {"type": "string", "enum": ["research"]},
                        "description": {"type": "string"},
                        "context": {"type": "object"}
                    },
                    "required": ["task_type", "description"]
                },
                output_schema={
                    "type": "object", 
                    "properties": {
                        "findings": {"type": "array"},
                        "summary": {"type": "string"},
                        "sources": {"type": "array"}
                    }
                },
                estimated_duration=180
            ),
            AgentCapability(
                name="analysis",
                description="Analyze data and provide insights",
                input_schema={
                    "type": "object",
                    "properties": {
                        "task_type": {"type": "string", "enum": ["analysis"]},
                        "description": {"type": "string"},
                        "context": {"type": "object"}
                    },
                    "required": ["task_type", "description"]
                },
                output_schema={
                    "type": "object",
                    "properties": {
                        "analysis": {"type": "string"},
                        "insights": {"type": "array"},
                        "recommendations": {"type": "array"}
                    }
                },
                estimated_duration=120
            )
        ]
    
    async def execute_task(self, task_type: TaskType, description: str, 
                          context: Dict[str, Any] = None) -> Dict[str, Any]:
        start_time = time.time()
        
        try:
            print(f"Executing {task_type.value} task: {description[:100]}...")
            
            if task_type == TaskType.RESEARCH:
                result = await self._research_task(description, context)
            elif task_type == TaskType.ANALYSIS:
                result = await self._analysis_task(description, context)
            elif task_type == TaskType.PLANNING:
                result = await self._planning_task(description, context)
            elif task_type == TaskType.WRITING:
                result = await self._writing_task(description, context)
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
    
    async def _research_task(self, description: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Research task using Gemini directly"""
        
        prompt = f"""
        Act as a senior researcher. Research the following topic thoroughly: {description}
        
        Context: {context or 'No additional context provided'}
        
        Provide:
        1. Key findings and insights
        2. Summary of important points
        3. Relevant sources or references
        
        Format your response as comprehensive research findings.
        """
        
        # Execute with Gemini
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(
            None, 
            lambda: self.model.generate_content(prompt)
        )
        
        content = response.text if response.text else "No response generated"
        
        return {
            "findings": [content],
            "summary": f"Research completed on: {description}",
            "sources": ["Gemini AI Research"],
            "raw_output": content
        }
    
    async def _analysis_task(self, description: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Analysis task using Gemini directly"""
        
        prompt = f"""
        Act as a senior data analyst. Analyze the following thoroughly: {description}
        
        Context: {context or 'No additional context provided'}
        
        Provide:
        1. Detailed analysis
        2. Key insights discovered
        3. Actionable recommendations
        
        Format your response as a comprehensive analysis report.
        """
        
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(
            None,
            lambda: self.model.generate_content(prompt)
        )
        
        content = response.text if response.text else "No response generated"
        
        return {
            "analysis": content,
            "insights": ["Analysis completed using Gemini AI"],
            "recommendations": ["Review detailed analysis for actionable items"],
            "raw_output": content
        }
    
    async def _planning_task(self, description: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Planning task using Gemini directly"""
        
        prompt = f"""
        Act as a strategic planner. Create a comprehensive plan for: {description}
        
        Context: {context or 'No additional context provided'}
        
        Include:
        1. Step-by-step action plan
        2. Timeline and milestones
        3. Resource requirements
        4. Risk considerations
        
        Format as a detailed strategic plan.
        """
        
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(
            None,
            lambda: self.model.generate_content(prompt)
        )
        
        content = response.text if response.text else "No response generated"
        
        return {
            "plan": content,
            "action_items": ["Review detailed plan for specific actions"],
            "timeline": "See plan for timeline details",
            "raw_output": content
        }
    
    async def _writing_task(self, description: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Writing task using Gemini directly"""
        
        prompt = f"""
        Act as a professional writer. Write high-quality content: {description}
        
        Context: {context or 'No additional context provided'}
        
        Ensure:
        1. Clear and engaging writing
        2. Proper structure and flow
        3. Relevant and accurate content
        
        Create compelling, well-structured content.
        """
        
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(
            None,
            lambda: self.model.generate_content(prompt)
        )
        
        content = response.text if response.text else "No response generated"
        
        return {
            "content": content,
            "word_count": len(content.split()) if content else 0,
            "type": "written_content",
            "raw_output": content
        }
    
    def get_capabilities(self) -> List[AgentCapability]:
        return self.capabilities