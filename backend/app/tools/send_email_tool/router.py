from fastapi import APIRouter
from .send_functions import router as send_router
from .oauth_callback import router as oauth_callback_router  # Add this import

router = APIRouter()
router.include_router(send_router)
router.include_router(oauth_callback_router)  # Add this line

__all__ = ["router"]