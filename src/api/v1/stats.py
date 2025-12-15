from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import db_session
from services import GetAppStatsService, GetLinkStatsService
from utils.fastapi_utils import MsgSpecJSONResponse

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
) -> MsgSpecJSONResponse:
    service = GetAppStatsService.build(session)
    stats = await service.execute()
    return MsgSpecJSONResponse(content=stats)


@router.get('/{short_code}')
async def get_link_stats(
    short_code: str,
    session: Annotated[
        AsyncSession,
        Depends(db_session.session_getter),
    ],
) -> MsgSpecJSONResponse:
    service = GetLinkStatsService.build(session)
    try:
        stats = await service.execute(short_code)
        return MsgSpecJSONResponse(content=stats)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        ) from e
