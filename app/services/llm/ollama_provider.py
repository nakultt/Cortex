import json
import ollama
from app.core.config import settings
from .base import LLMProvider

class OllamaProvider(LLMProvider):
    def __init__(self):
        print(f"Initializing Local AI (Ollama: {settings.OLLAMA_MODEL})")

    async def generate_answer(self, query: str, context: str = "") -> str:
        """
        Sends the user query + any retrieved context to the AI.
        """
        
        system_instruction = """
        You are the Cortex Core. 
        Answer the user's question clearly and concisely.
        If context is provided, prioritize that information.
        """
        
        message = [
            {
                "role": "system",
                "context": system_instruction
            },
            {
                "role": "user",
                "context": f"Context: {context}\n\nQustion: {query}"
            }
        ]   
             
        try:
            response = ollama.chat(
                model=settings.OLLAMA_MODEL,
                messages=message,
                options={
                    "temperature": 0.7, 
                    "num_ctx": 4096  #remember more conversation history
                }
            )
            
            return response['message']['content']
        
        except Exception as e:
            print(f"Ollama Error: {e}")
            return "My local brain is offline. Is Ollama running?"

    def extract_facts(self, text: str):
        """
        Reads text and extracts entities/relationships as JSON.
        """ 
        
        prompt = f"""
        Extract the key facts from this text: "{text}"
        Return ONLY a JSON list of relationships in this format:
        [
          {{"head": "Entity1", "type": "RELATION", "tail": "Entity2"}}
        ]
        Do not add any markown formatting like ```json. Just raw JSON.
        """
        
        try:
            response = ollama.chat(
                model=settings.OLLAMA_MODEL,
                messages=[
                    {
                        "role": "user", 
                        "content": prompt
                    }
                ],
                options={
                    "temperature": 0.0
                }
            )
            
            return json.loads(response['message']['content'])
        
        except Exception as e:
            print(f"Local Fact Extraction Error: {e}")
            return []