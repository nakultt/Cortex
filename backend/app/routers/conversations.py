"""
Conversations Router
CRUD operations for conversations and messages
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.models import Conversation, Message
from app.schemas import (
    ConversationCreate, 
    ConversationResponse, 
    ConversationList, 
    ConversationUpdate,
    MessageResponse
)

router = APIRouter(prefix="/api/conversations", tags=["Conversations"])


@router.post("", response_model=ConversationResponse)
async def create_conversation(
    request: ConversationCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create a new conversation"""
    conversation = Conversation(
        owner_id=request.user_id,
        title=request.title or "New Conversation"
    )
    db.add(conversation)
    await db.commit()
    await db.refresh(conversation)
    
    return conversation


@router.get("/{user_id}", response_model=ConversationList)
async def get_user_conversations(
    user_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get all conversations for a user"""
    result = await db.execute(
        select(Conversation)
        .where(Conversation.owner_id == user_id)
        .order_by(Conversation.updated_at.desc())
    )
    conversations = result.scalars().all()
    
    return ConversationList(
        conversations=[ConversationResponse.model_validate(c) for c in conversations],
        total=len(conversations)
    )


@router.get("/{conversation_id}/messages", response_model=list[MessageResponse])
async def get_conversation_messages(
    conversation_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get all messages in a conversation"""
    # Verify conversation exists
    result = await db.execute(
        select(Conversation).where(Conversation.id == conversation_id)
    )
    conversation = result.scalar_one_or_none()
    
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )
    
    # Get messages
    result = await db.execute(
        select(Message)
        .where(Message.conversation_id == conversation_id)
        .order_by(Message.created_at)
    )
    messages = result.scalars().all()
    
    return [MessageResponse.model_validate(m) for m in messages]


@router.put("/{conversation_id}", response_model=ConversationResponse)
async def update_conversation(
    conversation_id: int,
    request: ConversationUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Update conversation title"""
    result = await db.execute(
        select(Conversation).where(Conversation.id == conversation_id)
    )
    conversation = result.scalar_one_or_none()
    
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )
    
    conversation.title = request.title
    await db.commit()
    await db.refresh(conversation)
    
    return conversation


@router.delete("/{conversation_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_conversation(
    conversation_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Delete a conversation and all its messages"""
    result = await db.execute(
        select(Conversation).where(Conversation.id == conversation_id)
    )
    conversation = result.scalar_one_or_none()
    
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )
    
    await db.delete(conversation)
    await db.commit()
    
    return None
