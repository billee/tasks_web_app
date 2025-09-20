from fastapi import APIRouter
from .send_functions import router as send_router

router = APIRouter(prefix="/send-email")
router.include_router(send_router)

__all__ = ["router"]