from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import db_session
from dtos import AppStatsResponseDTO, LinkStatsResponseDTO
from services import GetAppStatsService, GetLinkStatsService

router = APIRouter(
    prefix='/stats',
    tags=['stats'],
)


@router.get('/overview')
async def get_app_stats(
    session: Annotated[
        AsyncSession,
        Depends(db_session.session_getter),
    ],
) -> AppStatsResponseDTO:
    service = GetAppStatsService.build(session)
    return await service.execute()


@router.get('/{short_code}')
async def get_link_stats(
    short_code: str,
    session: Annotated[
        AsyncSession,
        Depends(db_session.session_getter),
    ],
) -> LinkStatsResponseDTO:
    service = GetLinkStatsService.build(session)
    try:
        return await service.execute(short_code)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        ) from e
