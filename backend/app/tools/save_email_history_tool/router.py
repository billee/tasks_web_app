from fastapi import APIRouter
from .history_functions import router as history_router

# Remove the prefix here since we're already adding it in main.py
router = APIRouter()
router.include_router(history_router)

__all__ = ["router"]