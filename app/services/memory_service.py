from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct
from dotenv import load_dotenv
import os
from app.core.config import settings
import time

load_dotenv()

embedder = SentenceTransformer("all-MiniLM-L6-v2")

# connecting Qdrant
client = QdrantClient(url=settings.QDRANT_URL,
                      api_key=settings.QDRANT_API_KEY)

COLLECTION_NAME = "universal_history"

def initialize_memory():
    """ Creates the collection in Qdrant if it doesn't exist. """
    try:
        client.get_collection(collection_name=COLLECTION_NAME)
        print(f"Connected to Qdrant Collection: {COLLECTION_NAME}")
    except:
        client.create_collection(
            collection_name=COLLECTION_NAME,
            vectors_config={
                "size": 384,
                "distance": "Cosine"
            })
        print(f"Created Qdrant Collection: {COLLECTION_NAME}")
        
def check_cache(query: str):
    """
    Searches Memory for a similar question.
    Returns the answer if similarity > 90%.
    """
    # converts text to number vector of size 384 numbers
    vector = embedder.encode(query).tolist()
    
    # searches Qdrant for similar vectors
    hits = client.search(
        collection_name=COLLECTION_NAME,
        query_vector=vector,
        limit=1
    )
    
    if hits:
        best_match = hits[0]
        score = best_match.score
        
        if best_match.score > settings.THRESHOLD:
            return best_match.payload["answer"]
        else:
            print(f"Cache MISS. Best match was only {score:.2f}")
    
    return None

def save_to_cache(query: str, answer: str):
    """
    Saves a new Q&A pair to the memory.
    """
    vector = embedder.encode(query).tolist()
    
    unique_id = int(time.time() * 1000) 
    
    client.upsert(
        collection_name=COLLECTION_NAME,
        points=[
            PointStruct(
                id=unique_id,
                vector=vector,
                payload={
                    "question": query,
                    "answer": answer,
                    "timestamp": time.time()
                }
            )
        ]
    )
    print(f"Saved to Memory: '{query}'")

initialize_memory()
