from fastapi import APIRouter
from .lookup_functions import router as lookup_router

router = APIRouter(prefix="/lookup-contact")
router.include_router(lookup_router)

__all__ = ["router"]