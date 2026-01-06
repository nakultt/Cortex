"""
Chat Router
Handles chat messages with AI integration
"""
from fastapi import APIRouter, BackgroundTasks, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models import Conversation, Message
from app.schemas import ChatRequest, ChatResponse
from app.services import memory_service
from app.services import graph_service
from app.services import distiller
from app.services.llm import llm_service

router = APIRouter(prefix="/api", tags=["Chat"])


def extract_entities_simple(query: str) -> list[str]:
    """Simple entity extraction from query using keyword matching."""
    stop_words = {'what', 'who', 'where', 'when', 'why', 'how', 'is', 'are', 
                  'the', 'a', 'an', 'of', 'in', 'on', 'at', 'to', 'for',
                  'tell', 'me', 'about', 'can', 'you', 'please', 'do', 'does'}
    
    words = query.lower().replace('?', '').replace('.', '').split()
    entities = [word.capitalize() for word in words if word not in stop_words and len(word) > 2]
    return entities


@router.post("/chat", response_model=ChatResponse)
async def chat_endpoint(
    request: ChatRequest, 
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
):
    """
    Send a chat message and get AI response.
    Optionally saves to a conversation.
    """
    user_query = request.message
    conversation_id = request.conversation_id
    
    # If no conversation_id, create a new conversation
    if conversation_id is None and request.user_id:
        # Create new conversation with first message as title
        title = user_query[:50] + "..." if len(user_query) > 50 else user_query
        conversation = Conversation(
            owner_id=request.user_id,
            title=title
        )
        db.add(conversation)
        await db.commit()
        await db.refresh(conversation)
        conversation_id = conversation.id
    
    # Save user message to database
    if conversation_id:
        user_message = Message(
            conversation_id=conversation_id,
            role="user",
            content=user_query
        )
        db.add(user_message)
        await db.commit()
    
    # --- STEP 1: CHECK QDRANT (Memory Cache) ---
    cached_answer = memory_service.check_cache(user_query)
    if cached_answer:
        # Save assistant response to database
        if conversation_id:
            assistant_message = Message(
                conversation_id=conversation_id,
                role="assistant",
                content=cached_answer
            )
            db.add(assistant_message)
            await db.commit()
        
        return ChatResponse(
            message=cached_answer,
            conversation_id=conversation_id
        )

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
    
    # Save assistant response to database
    if conversation_id:
        assistant_message = Message(
            conversation_id=conversation_id,
            role="assistant",
            content=new_answer
        )
        db.add(assistant_message)
        await db.commit()
    
    return ChatResponse(
        message=new_answer,
        conversation_id=conversation_id,
        raw_response=new_answer if request.smart_mode else None
    )
