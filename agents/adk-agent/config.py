import os
from typing import Optional
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Agent identity
    AGENT_ID: str = os.getenv("AGENT_ID", "adk-agent")
    AGENT_NAME: str = os.getenv("AGENT_NAME", "ADK Data Processing Agent")
    AGENT_TYPE: str = os.getenv("AGENT_TYPE", "adk")
    
    # Server settings
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8083"))
    
    # Google Gemini API
    GOOGLE_API_KEY: Optional[str] = os.getenv("GOOGLE_API_KEY")
    GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-2.0-flash-exp")
    
    # ADK settings
    MAX_EXECUTION_TIME: int = int(os.getenv("MAX_EXECUTION_TIME", "300"))
    MAX_DATASET_SIZE: int = int(os.getenv("MAX_DATASET_SIZE", "10000"))  # rows
    
    # Logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")