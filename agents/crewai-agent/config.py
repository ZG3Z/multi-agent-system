import os
from typing import Optional
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    # Agent identity
    AGENT_ID: str = os.getenv("AGENT_ID", "crewai-agent")
    AGENT_NAME: str = os.getenv("AGENT_NAME", "CrewAI Research Agent")
    AGENT_TYPE: str = os.getenv("AGENT_TYPE", "crewai")
    
    # Server settings
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8080"))
    
    # Google Gemini API
    GOOGLE_API_KEY: Optional[str] = os.getenv("GOOGLE_API_KEY")
    GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-2.0-flash-exp")
    
    # CrewAI settings
    CREW_VERBOSE: bool = os.getenv("CREW_VERBOSE", "true").lower() == "true"
    MAX_EXECUTION_TIME: int = int(os.getenv("MAX_EXECUTION_TIME", "300"))
    
    # Logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")