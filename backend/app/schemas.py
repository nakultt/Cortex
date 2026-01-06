"""
Pydantic Schemas
Request/Response models for API endpoints
"""
from datetime import datetime
from pydantic import BaseModel, EmailStr


# ============== Auth Schemas ==============

class SignupRequest(BaseModel):
    email: EmailStr
    password: str
    name: str | None = None


class LoginRequest(BaseModel):
    email: EmailStr
    password: str
    remember_me: bool = False


class UserResponse(BaseModel):
    id: int
    email: str
    name: str | None
    token: str | None = None
    created_at: datetime | None = None

    class Config:
        from_attributes = True


class UserUpdate(BaseModel):
    email: EmailStr | None = None
    password: str | None = None
    name: str | None = None


# ============== Chat Schemas ==============

class ChatRequest(BaseModel):
    user_id: int
    message: str
    smart_mode: bool = False
    conversation_id: int | None = None


class ChatResponse(BaseModel):
    message: str
    conversation_id: int | None = None
    raw_response: str | None = None


# ============== Conversation Schemas ==============

class ConversationCreate(BaseModel):
    user_id: int
    title: str | None = None


class ConversationResponse(BaseModel):
    id: int
    title: str
    owner_id: int
    created_at: datetime
    updated_at: datetime | None = None

    class Config:
        from_attributes = True


class ConversationList(BaseModel):
    conversations: list[ConversationResponse]
    total: int


class ConversationUpdate(BaseModel):
    title: str


# ============== Message Schemas ==============

class MessageResponse(BaseModel):
    id: int
    conversation_id: int
    role: str
    content: str
    created_at: datetime

    class Config:
        from_attributes = True
