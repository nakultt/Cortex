import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "Cortex"
    VERSION: str = "1.0.0"
    
    DATABASE_URL: str
    
    QDRANT_URL: str
    QDRANT_API_KEY: str
    THRESHOLD: float = 0.9
    
    NEO4J_URI: str
    NEO4J_USERNAME: str
    NEO4J_PASSWORD: str
    NEO4J_DATABASE: str
    AURA_INSTANCEID: str
    AURA_INSTANCENAME: str
    
    GROQ_API_KEY: str
    GROQ_MODEL: str = "llama-3.3-70b-versatile"
    
    OLLAMA_URL: str = "http://localhost:11434/api/generate"
    OLLAMA_MODEL: str = "qwen3"
    
    USE_LOCAL_AI:bool
    
    # JWT Settings
    JWT_SECRET: str = "cortex-secret-key-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_HOURS: int = 24
    
    class Config:
        env_file = "../.env"
        env_file_encoding = "utf-8"
        extra = "ignore"
        
settings = Settings() #type: ignore