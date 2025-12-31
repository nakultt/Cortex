from app.core.config import settings
from .base import LLMProvider

llm_service: LLMProvider = None

if settings.USE_LOCAL_AI:
    from .ollama_provider import OllamaProvider
    llm_service = OllamaProvider()
else:
    from .groq_provider import GroqProvider
    llm_service = GroqProvider()
