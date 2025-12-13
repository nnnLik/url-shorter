from fastapi import APIRouter

from .health import router as health_router
from .link import router as link_router
from .stats import router as stats_router

router = APIRouter(
    prefix='/v1',
)

router.include_router(health_router)
router.include_router(link_router)
router.include_router(stats_router)
