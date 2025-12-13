from fastapi import APIRouter

from .link import router as link_router

router = APIRouter(
    prefix="/v1",
)

router.include_router(link_router)
