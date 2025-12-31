from abc import ABC, abstractmethod
from typing import List, Dict, Any

class LLMProvider(ABC):
    """
    The Interface: Every AI provider must implement these methods.
    """
    
    @abstractmethod
    async def generate_answer(self, query: str, context: str = "") -> str:
        """Generates a text response based on query and context."""
        pass

    @abstractmethod
    def extract_facts(self, text: str) -> List[Dict[str, Any]]:
        """Extracts structured facts (Head-Relation-Tail) from text."""
        pass    
