from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional
from datetime import datetime
from enum import Enum

class TaskType(str, Enum):
    DATA_TRANSFORMATION = "data_transformation"
    DATA_ANALYSIS = "data_analysis"
    DATA_VALIDATION = "data_validation"
    DATA_AGGREGATION = "data_aggregation"

class TaskRequest(BaseModel):
    task_type: TaskType
    description: str
    context: Optional[Dict[str, Any]] = None
    collaborators: Optional[Dict[str, str]] = None
    timeout: Optional[int] = Field(default=300, description="Timeout in seconds")

class TaskResult(BaseModel):
    success: bool
    result: Dict[str, Any]
    agent_id: str = "adk-agent"
    execution_time: float
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    error: Optional[str] = None

class AgentCapability(BaseModel):
    name: str
    description: str
    input_schema: Dict[str, Any]
    output_schema: Dict[str, Any]
    estimated_duration: int

class AgentStatus(BaseModel):
    status: str = "healthy"
    agent_id: str = "adk-agent"
    agent_type: str = "adk"
    uptime: float
    active_tasks: int = 0
    capabilities_count: int
    timestamp: datetime = Field(default_factory=datetime.utcnow)