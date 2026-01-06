from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct
from dotenv import load_dotenv
from app.core.config import settings
import time

load_dotenv()

# Lazy initialization - don't connect at import time
_client = None
_embedder = None

COLLECTION_NAME = "universal_history"

def _get_embedder():
    """Lazy load the sentence transformer model."""
    global _embedder
    if _embedder is None:
        print("📦 Loading sentence transformer model...")
        _embedder = SentenceTransformer("all-MiniLM-L6-v2")
        print("✅ Model loaded: all-MiniLM-L6-v2")
    return _embedder

def _get_client():
    """Lazy load the Qdrant client."""
    global _client
    if _client is None:
        print(f"🔌 Connecting to Qdrant at {settings.QDRANT_URL}...")
        _client = QdrantClient(
            url=settings.QDRANT_URL,
            api_key=settings.QDRANT_API_KEY if settings.QDRANT_API_KEY else None
        )
        _initialize_collection()
    return _client

def _initialize_collection():
    """ Creates the collection in Qdrant if it doesn't exist. """
    global _client
    try:
        _client.get_collection(collection_name=COLLECTION_NAME)
        print(f"✅ Connected to Qdrant Collection: {COLLECTION_NAME}")
    except Exception:
        _client.create_collection(
            collection_name=COLLECTION_NAME,
            vectors_config={
                "size": 384,
                "distance": "Cosine"
            })
        print(f"📁 Created Qdrant Collection: {COLLECTION_NAME}")
        
def check_cache(query: str):
    """
    Searches Memory for a similar question.
    Returns the answer if similarity > threshold.
    """
    try:
        client = _get_client()
        embedder = _get_embedder()
        
        print(f"\n🔍 MEMORY CHECK")
        print(f"   Query: '{query[:80]}...'")
        print(f"   Threshold: {settings.THRESHOLD}")
        
        # converts text to number vector of size 384 numbers
        vector = embedder.encode(query).tolist()
        
        # searches Qdrant for similar vectors
        result = client.query_points(
            collection_name=COLLECTION_NAME,
            query=vector,
            limit=3  # Get top 3 for logging
        )
        hits = result.points if result else []
        
        print(f"   Found {len(hits)} potential matches")
        
        if hits:
            for i, hit in enumerate(hits):
                score = hit.score
                question = hit.payload.get("question", "?")[:50]
                print(f"   [{i+1}] Score: {score:.4f} | Q: '{question}...'")
            
            best_match = hits[0]
            score = best_match.score
            
            if score > settings.THRESHOLD:
                cached_answer = best_match.payload["answer"]
                print(f"\n   ✅ CACHE HIT! Score {score:.4f} > {settings.THRESHOLD}")
                print(f"   📤 Returning cached answer: '{cached_answer[:100]}...'")
                return cached_answer
            else:
                print(f"\n   ❌ CACHE MISS. Best score {score:.4f} < {settings.THRESHOLD}")
        else:
            print(f"   ❌ CACHE MISS. No matches found.")
        
        return None
    except Exception as e:
        print(f"   ⚠️ Cache check failed: {e}")
        return None

def save_to_cache(query: str, answer: str):
    """
    Saves a new Q&A pair to the memory.
    """
    try:
        client = _get_client()
        embedder = _get_embedder()
        
        print(f"\n💾 SAVING TO MEMORY")
        print(f"   Q: '{query[:80]}...'")
        print(f"   A: '{answer[:80]}...'")
        
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
        print(f"   ✅ Saved with ID: {unique_id}")
    except Exception as e:
        print(f"   ⚠️ Failed to save to cache: {e}")
