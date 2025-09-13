from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

# Import routers
from app.auth import router as auth_router
from app import models
from app.database import engine
from app.admin import router as admin_router

# Create database tables
models.Base.metadata.create_all(bind=engine)

# Load environment variables from root directory
import os
from pathlib import Path

# Get the root directory (two levels up from this file)
root_dir = Path(__file__).parent.parent.parent
env_path = root_dir / ".env"
load_dotenv(dotenv_path=str(env_path))

# Database setup
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    DATABASE_URL = "postgresql://localhost/your_app_db"  # fallback

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


# Create FastAPI app
app = FastAPI(title="Email Categorizer API", version="1.0.0")

# Configure CORS
cors_origins = os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth_router)
app.include_router(admin_router)

# Basic health check endpoint
@app.get("/")
async def root():
    return {"message": "Email Categorizer API is running!"}

@app.get("/api/health")
async def health_check():
    return {"status": "healthy", "message": "Server is running successfully"}

@app.on_event("startup")
def create_tables():
    Base.metadata.create_all(bind=engine)

@app.get("/")
def read_root():
    return {"message": "FastAPI backend is running!"}

# @app.get("/health")
# def health_check():
#     return {"status": "healthy", "database": "connected"}