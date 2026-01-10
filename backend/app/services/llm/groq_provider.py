import json
from groq import Groq
from app.core.config import settings
from .base import LLMProvider

client = Groq(
    api_key=settings.GROQ_API_KEY,
)

class GroqProvider(LLMProvider):
    def __init__(self):
        print(f"Initializing Cloud AI (Groq: {settings.GROQ_MODEL})")
        self.client = Groq(
            api_key=settings.GROQ_API_KEY,
        )
        
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
                "content": system_instruction
            },
            {
                "role": "user",
                "content": f"Context: {context}\n\nQuestion: {query}"
            }
        ]

        try:
            print(f"🚀 Calling Groq API with query: {query[:50]}...")
            chat_completion = client.chat.completions.create(
                messages=message,
                model=settings.GROQ_MODEL,
                temperature= 0.7
            )
            response = chat_completion.choices[0].message.content
            print(f"✅ Groq response received: {response[:100]}...")
            return response

        except Exception as e:
            print(f"❌ Groq API Error : {e}")
            return "I'm sorry, my brain is offline right now."

    async def extract_facts(self, text: str):
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
            response = client.chat.completions.create(
                messages= [
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                model=settings.GROQ_MODEL,
                temperature=0.0
            )

            return json.loads(response.choices[0].message.content)

        except Exception as e:
            print(f"Fact Extraction Error: {e}")
            return []