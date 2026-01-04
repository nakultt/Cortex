from fastapi import APIRouter, BackgroundTasks
from pydantic import BaseModel
from app.services import memory_service
from app.services import graph_service
from app.services import distiller
from app.services.llm import llm_service

router = APIRouter()

class ChatRequest(BaseModel):
    query: str


def extract_entities_simple(query: str) -> list[str]:
    """Simple entity extraction from query using keyword matching."""
    stop_words = {'what', 'who', 'where', 'when', 'why', 'how', 'is', 'are', 
                  'the', 'a', 'an', 'of', 'in', 'on', 'at', 'to', 'for',
                  'tell', 'me', 'about', 'can', 'you', 'please', 'do', 'does'}
    
    words = query.lower().replace('?', '').replace('.', '').split()
    entities = [word.capitalize() for word in words if word not in stop_words and len(word) > 2]
    return entities


@router.post("/chat")
async def chat_endpoint(request: ChatRequest, background_tasks: BackgroundTasks):
    user_query = request.query
    
    # --- STEP 1: CHECK QDRANT (Memory Cache) ---
    cached_answer = memory_service.check_cache(user_query)
    if cached_answer:
        return {
            "response": cached_answer, 
            "source": "qdrant_cache"
        }

    # --- STEP 2: CHECK GRAPH (Neo4j Facts) ---
    graph_context = ""
    entities = extract_entities_simple(user_query)
    for entity in entities:
        try:
            facts = graph_service.get_entity_facts(entity)
            if facts:
                graph_context += "\n".join(facts) + "\n"
        except Exception as e:
            print(f"Graph lookup error for '{entity}': {e}")

    # --- STEP 3: GENERATE ANSWER (LLM) ---
    new_answer = await llm_service.generate_answer(user_query, context=graph_context)
    
    # --- STEP 4: SAVE TO QDRANT (Background) ---
    background_tasks.add_task(memory_service.save_to_cache, user_query, new_answer)
    
    # --- STEP 5: SAVE TO GRAPH (Background) ---
    background_tasks.add_task(distiller.distill_conversation, user_query, new_answer)
    
    return {
        "response": new_answer, 
        "source": "generated",
        "graph_context_found": bool(graph_context)
    }
