"""
A2A Communication Client
"""

import asyncio
import httpx
import uuid
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
from pydantic import BaseModel, Field
from enum import Enum

# A2A Protocol Definitions
class A2AMessageType(str, Enum):
    """A2A message types"""
    HEALTH_CHECK = "health_check"
    GET_CAPABILITIES = "get_capabilities"
    EXECUTE_TASK = "execute_task"
    DELEGATE_TASK = "delegate_task"
    SHARE_CONTEXT = "share_context"

class A2AMessage(BaseModel):
    """A2A message format"""
    message_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    message_type: A2AMessageType
    sender_id: str
    receiver_id: Optional[str] = None
    payload: Dict[str, Any] = Field(default_factory=dict)
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    correlation_id: Optional[str] = None

class A2AResponse(BaseModel):
    """A2A response format"""
    success: bool
    message_id: str
    sender_id: str
    payload: Dict[str, Any] = Field(default_factory=dict)
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    error: Optional[str] = None

class A2AClient:
    """A2A communication client"""
    
    def __init__(self, agent_id: str, agent_type: str):
        """
        Initialize A2A client
        
        Args:
            agent_id: Unique identifier for this agent
            agent_type: Type of agent (crewai, langraph, adk)
        """
        self.agent_id = agent_id
        self.agent_type = agent_type
        self.logger = logging.getLogger(f"a2a.{agent_id}")
        self.timeout = 30.0
        
    async def send_message(self, target_url: str, message: A2AMessage) -> A2AResponse:
        """
        Send A2A message to another agent
        
        Args:
            target_url: Target agent's base URL (e.g., "http://localhost:8082")
            message: A2A message to send
            
        Returns:
            A2AResponse with the result
        """
        endpoint = f"{target_url}/a2a/message"
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                self.logger.info(f"Sending {message.message_type} to {target_url}")
                
                response = await client.post(
                    endpoint,
                    json=message.dict(),
                    headers={"Content-Type": "application/json"}
                )
                
                if response.status_code == 200:
                    result_data = response.json()
                    self.logger.info(f"Received response from {target_url}")
                    
                    return A2AResponse(
                        success=True,
                        message_id=result_data.get("message_id", "unknown"),
                        sender_id=result_data.get("sender_id", "unknown"),
                        payload=result_data.get("payload", {}),
                        timestamp=datetime.utcnow().isoformat()
                    )
                else:
                    error_msg = f"HTTP {response.status_code}: {response.text}"
                    self.logger.error(f"A2A request failed: {error_msg}")
                    
                    return A2AResponse(
                        success=False,
                        message_id=message.message_id,
                        sender_id=self.agent_id,
                        error=error_msg
                    )
                    
        except httpx.TimeoutException:
            error_msg = f"Timeout communicating with {target_url}"
            self.logger.error(error_msg)
            return A2AResponse(
                success=False,
                message_id=message.message_id,
                sender_id=self.agent_id,
                error=error_msg,
                timestamp=datetime.utcnow().isoformat()
            )
        except Exception as e:
            error_msg = f"Communication error: {str(e)}"
            self.logger.error(error_msg)
            return A2AResponse(
                success=False,
                message_id=message.message_id,
                sender_id=self.agent_id,
                error=error_msg
            )
    
    async def health_check(self, target_url: str) -> A2AResponse:
        """Check if another agent is healthy"""
        message = A2AMessage(
            message_type=A2AMessageType.HEALTH_CHECK,
            sender_id=self.agent_id,
            payload={"agent_type": self.agent_type}
        )
        return await self.send_message(target_url, message)
    
    async def get_capabilities(self, target_url: str) -> A2AResponse:
        """Get capabilities from another agent"""
        message = A2AMessage(
            message_type=A2AMessageType.GET_CAPABILITIES,
            sender_id=self.agent_id,
            payload={}
        )
        return await self.send_message(target_url, message)
    
    async def execute_task(self, target_url: str, task_data: Dict[str, Any]) -> A2AResponse:
        """Execute task on another agent"""
        message = A2AMessage(
            message_type=A2AMessageType.EXECUTE_TASK,
            sender_id=self.agent_id,
            payload=task_data,
            correlation_id=str(uuid.uuid4())
        )
        return await self.send_message(target_url, message)
    
    async def delegate_task(self, target_url: str, task_description: str, 
                           task_data: Dict[str, Any], required_capability: str = None) -> A2AResponse:
        """Delegate a task to another agent"""
        message = A2AMessage(
            message_type=A2AMessageType.DELEGATE_TASK,
            sender_id=self.agent_id,
            payload={
                "task_description": task_description,
                "task_data": task_data,
                "required_capability": required_capability,
                "delegated_by": self.agent_id
            },
            correlation_id=str(uuid.uuid4())
        )
        return await self.send_message(target_url, message)
    
    async def share_context(self, target_url: str, context_data: Dict[str, Any], 
                           context_type: str = "general") -> A2AResponse:
        """Share context information with another agent"""
        message = A2AMessage(
            message_type=A2AMessageType.SHARE_CONTEXT,
            sender_id=self.agent_id,
            payload={
                "context_data": context_data,
                "context_type": context_type,
                "shared_by": self.agent_id
            }
        )
        return await self.send_message(target_url, message)
    
    async def find_capable_agent(self, agent_urls: List[str], required_capability: str) -> Optional[str]:
        """
        Find an agent with a specific capability
        
        Args:
            agent_urls: List of agent URLs to check
            required_capability: Capability name to look for
            
        Returns:
            URL of first agent with the capability, or None
        """
        for url in agent_urls:
            try:
                response = await self.get_capabilities(url)
                if response.success:
                    capabilities = response.payload.get("capabilities", [])
                    for cap in capabilities:
                        if cap.get("name") == required_capability:
                            self.logger.info(f"Found agent with {required_capability} at {url}")
                            return url
            except Exception as e:
                self.logger.warning(f"Failed to check capabilities at {url}: {e}")
                continue
        
        self.logger.warning(f"No agent found with capability: {required_capability}")
        return None
    
    async def broadcast_to_all(self, agent_urls: List[str], message: A2AMessage) -> List[A2AResponse]:
        """
        Broadcast message to multiple agents
        
        Args:
            agent_urls: List of agent URLs
            message: Message to broadcast
            
        Returns:
            List of responses from all agents
        """
        tasks = [self.send_message(url, message) for url in agent_urls]
        responses = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Filter out exceptions and return only A2AResponse objects
        valid_responses = []
        for response in responses:
            if isinstance(response, A2AResponse):
                valid_responses.append(response)
            else:
                # Log exceptions but don't fail the broadcast
                self.logger.warning(f"Broadcast failed to one agent: {response}")
                
        return valid_responses

class A2AMessageHandler:
    """Handler for incoming A2A messages"""
    
    def __init__(self, agent_id: str, agent_type: str):
        self.agent_id = agent_id
        self.agent_type = agent_type
        self.logger = logging.getLogger(f"a2a_handler.{agent_id}")
        
    async def handle_message(self, message: A2AMessage, agent_logic) -> A2AResponse:
        """
        Handle incoming A2A message
        
        Args:
            message: Received A2A message
            agent_logic: Agent's logic instance (for executing tasks)
            
        Returns:
            A2AResponse
        """
        try:
            self.logger.info(f"Handling {message.message_type} from {message.sender_id}")
            
            if message.message_type == A2AMessageType.HEALTH_CHECK:
                return await self._handle_health_check(message)
            
            elif message.message_type == A2AMessageType.GET_CAPABILITIES:
                return await self._handle_get_capabilities(message, agent_logic)
            
            elif message.message_type == A2AMessageType.EXECUTE_TASK:
                return await self._handle_execute_task(message, agent_logic)
            
            elif message.message_type == A2AMessageType.DELEGATE_TASK:
                return await self._handle_delegate_task(message, agent_logic)
            
            elif message.message_type == A2AMessageType.SHARE_CONTEXT:
                return await self._handle_share_context(message)
            
            else:
                return A2AResponse(
                    success=False,
                    message_id=message.message_id,
                    sender_id=self.agent_id,
                    error=f"Unknown message type: {message.message_type}",
                    timestamp=datetime.utcnow().isoformat()
                )
                
        except Exception as e:
            self.logger.error(f"Error handling A2A message: {e}")
            return A2AResponse(
                success=False,
                message_id=message.message_id,
                sender_id=self.agent_id,
                error=f"Message handling failed: {str(e)}",
                timestamp=datetime.utcnow().isoformat()
            )
    
    async def _handle_health_check(self, message: A2AMessage) -> A2AResponse:
        """Handle health check request"""
        return A2AResponse(
            success=True,
            message_id=message.message_id,
            sender_id=self.agent_id,
            payload={
                "status": "healthy",
                "agent_id": self.agent_id,
                "agent_type": self.agent_type,
                "timestamp": datetime.utcnow().isoformat()
            },
            timestamp=datetime.utcnow().isoformat()
        )
    
    async def _handle_get_capabilities(self, message: A2AMessage, agent_logic) -> A2AResponse:
        """Handle capabilities query"""
        try:
            capabilities = agent_logic.get_capabilities()
            return A2AResponse(
                success=True,
                message_id=message.message_id,
                sender_id=self.agent_id,
                payload={
                    "capabilities": [cap.dict() for cap in capabilities],
                    "agent_type": self.agent_type
                },
                timestamp=datetime.utcnow().isoformat()
            )
        except Exception as e:
            return A2AResponse(
                success=False,
                message_id=message.message_id,
                sender_id=self.agent_id,
                error=f"Failed to get capabilities: {str(e)}",
                timestamp=datetime.utcnow().isoformat()
            )
    
    async def _handle_execute_task(self, message: A2AMessage, agent_logic) -> A2AResponse:
        """Handle task execution request"""
        try:
            task_data = message.payload
            
            # Extract task parameters
            task_type = task_data.get("task_type")
            description = task_data.get("description", "")
            context = task_data.get("context", {})
            
            if not task_type:
                return A2AResponse(
                    success=False,
                    message_id=message.message_id,
                    sender_id=self.agent_id,
                    error="Missing task_type in task data"
                )
            
            # Execute task using agent's logic
            result = await agent_logic.execute_task(task_type, description, context)
            
            return A2AResponse(
                success=result.get("success", False),
                message_id=message.message_id,
                sender_id=self.agent_id,
                payload={
                    "task_result": result,
                    "executed_by": self.agent_id
                },
                error=result.get("error") if not result.get("success", False) else None,
                timestamp=datetime.utcnow().isoformat()
            )
            
        except Exception as e:
            return A2AResponse(
                success=False,
                message_id=message.message_id,
                sender_id=self.agent_id,
                error=f"Task execution failed: {str(e)}",
                timestamp=datetime.utcnow().isoformat()
            )
    
    async def _handle_delegate_task(self, message: A2AMessage, agent_logic) -> A2AResponse:
        """Handle task delegation request"""
        # For now, treat delegation the same as execution
        # In future, could add more sophisticated delegation logic
        return await self._handle_execute_task(message, agent_logic)
    
    async def _handle_share_context(self, message: A2AMessage) -> A2AResponse:
        """Handle context sharing"""
        context_data = message.payload.get("context_data", {})
        context_type = message.payload.get("context_type", "general")
        
        # For now, just acknowledge receipt
        # In future, could store context for use in subsequent tasks
        self.logger.info(f"Received {context_type} context from {message.sender_id}")
        
        return A2AResponse(
            success=True,
            message_id=message.message_id,
            sender_id=self.agent_id,
            payload={
                "context_received": True,
                "context_type": context_type,
                "received_by": self.agent_id
            },
            timestamp=datetime.utcnow().isoformat()
        )

# Utility functions for easy integration
def create_a2a_client(agent_id: str, agent_type: str) -> A2AClient:
    """Factory function to create A2A client"""
    return A2AClient(agent_id, agent_type)

def create_a2a_handler(agent_id: str, agent_type: str) -> A2AMessageHandler:
    """Factory function to create A2A message handler"""
    return A2AMessageHandler(agent_id, agent_type)