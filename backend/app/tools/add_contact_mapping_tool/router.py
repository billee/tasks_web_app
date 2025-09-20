from fastapi import APIRouter
from .mapping_functions import router as mapping_router

router = APIRouter(prefix="/contact-mapping")
router.include_router(mapping_router)

__all__ = ["router"]