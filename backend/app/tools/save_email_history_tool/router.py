from fastapi import APIRouter
from .history_functions import router as history_router

router = APIRouter(prefix="/email-history")
router.include_router(history_router)

__all__ = ["router"]