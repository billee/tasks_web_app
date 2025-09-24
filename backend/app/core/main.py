from pathlib import Path
import os
from dotenv import load_dotenv

# Get the root directory (three levels up from this file)
root_dir = Path(__file__).parent.parent.parent
env_path = root_dir / ".env"
load_dotenv(dotenv_path=str(env_path))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Import routers - UPDATED PATHS
from app.common.auth import router as auth_router
from app.common import models
from app.common.database import engine
from app.core.admin import router as admin_router

# Import individual tool routers
from app.tools.send_email_tool.router import router as send_email_router
from app.tools.lookup_contact_tool.router import router as lookup_contact_router
from app.tools.save_email_history_tool.router import router as save_history_router
from app.tools.add_contact_mapping_tool.router import router as contact_mapping_router
from app.tools.chat_router import router as chat_router

# Import read_gmail_router with error handling
try:
    from app.tools.read_gmail_tool.router import router as read_gmail_router
    READ_GMAIL_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Could not import read_gmail_tool router: {e}")
    READ_GMAIL_AVAILABLE = False
    # Create a dummy router for read_gmail_router
    from fastapi import APIRouter
    read_gmail_router = APIRouter()

# Create database tables
models.Base.metadata.create_all(bind=engine)

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

# Include individual tool routers with appropriate prefixes
app.include_router(chat_router, prefix="/email-tools")
app.include_router(send_email_router, prefix="/email-tools")
app.include_router(lookup_contact_router, prefix="/email-tools")
app.include_router(save_history_router, prefix="/email-tools")
app.include_router(contact_mapping_router, prefix="/email-tools")

# Only include read_gmail_router if it's available
if READ_GMAIL_AVAILABLE:
    app.include_router(read_gmail_router, prefix="/email-tools", tags=["email-tools"])
else:
    # Add a placeholder endpoint for read_gmail_tool
    @app.get("/email-tools/test-gmail")
    async def test_gmail_endpoint():
        return {"message": "Gmail tool is not available due to import errors"}

# Basic health check endpoint
@app.get("/")
async def root():
    return {"message": "Email Categorizer API is running!"}

@app.get("/api/health")
async def health_check():
    return {"status": "healthy", "message": "Server is running successfully"}