from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
from dotenv import load_dotenv

# Import routers
from app.auth import router as auth_router
from app import models
from app.database import engine  # Use the engine from database.py
from app.admin import router as admin_router
from app.email_tools import router as email_tools_router  # ADD THIS LINE

# Create database tables
models.Base.metadata.create_all(bind=engine)

# Load environment variables from root directory
from pathlib import Path



# Get the root directory (two levels up from this file)
root_dir = Path(__file__).parent.parent.parent
env_path = root_dir / ".env"
load_dotenv(dotenv_path=str(env_path))

print(f"OpenAI API Key: {os.getenv('OPENAI_API_KEY') is not None}")
print(f"Resend API Key: {os.getenv('RESEND_API_KEY') is not None}")
print(f"Default From Email: {os.getenv('DEFAULT_FROM_EMAIL')}")

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
app.include_router(email_tools_router)  # ADD THIS LINE

# Basic health check endpoint
@app.get("/")
async def root():
    return {"message": "Email Categorizer API is running!"}

@app.get("/api/health")
async def health_check():
    return {"status": "healthy", "message": "Server is running successfully"}