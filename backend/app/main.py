"""
Cortex Backend - FastAPI Application
FastAPI Backend with Vector Search and Graph DB
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import init_db
from app.routers import chat, auth, conversations


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan - initialize database on startup"""
    await init_db()
    yield


app = FastAPI(
    title="Cortex API",
    description="FastAPI Backend with Vector Search and Graph DB",
    version="0.1.0",
    lifespan=lifespan
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register Routers
app.include_router(auth.router)
app.include_router(chat.router)
app.include_router(conversations.router)


@app.get("/")
async def root():
    """Health check endpoint"""
    return {"status": "healthy", "message": "Cortex API is running"}


@app.get("/health")
async def health_check():
    """Detailed health check"""
    return {
        "status": "ok",
        "service": "Cortex",
        "version": "0.1.0"
    }
