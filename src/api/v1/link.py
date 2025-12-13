from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import db_session
from daos import LinkDAO
from dtos import CreateLinkRequestDTO, LinkStatsResponseDTO, AppStatsResponseDTO
from services import CreateLinkService, RedirectService
from utils.fastapi_utils import MsgSpecJSONResponse, decode_msgspec

router = APIRouter(
    prefix="/links",
    tags=["links"],
)


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_link(
    http_request: Request,
    session: Annotated[AsyncSession, Depends(db_session.session_getter)],
) -> Response:
    request = await decode_msgspec(http_request, CreateLinkRequestDTO)
    service = CreateLinkService.build(session)

    try:
        result = await service.execute(
            original_url=request.original_url,
            expires_at=request.expires_at,
        )
        return MsgSpecJSONResponse(content=result, status_code=status.HTTP_201_CREATED)
    except CreateLinkService.CreateLinkServiceError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/stats/overview")
async def get_app_stats(
    session: Annotated[
        AsyncSession,
        Depends(db_session.session_getter),
    ],
) -> MsgSpecJSONResponse:
    """Получает общую статистику приложения."""
    link_dao = LinkDAO(session)
    stats = await link_dao.get_app_stats()
    return MsgSpecJSONResponse(content=stats)


@router.get("/{short_code}/stats")
async def get_link_stats(
    short_code: str,
    session: Annotated[
        AsyncSession,
        Depends(db_session.session_getter),
    ],
) -> MsgSpecJSONResponse:
    """Получает статистику по конкретной ссылке."""
    link_dao = LinkDAO(session)
    stats = await link_dao.get_link_stats_by_code(short_code)

    if stats is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Link not found",
        )

    return MsgSpecJSONResponse(content=stats)


@router.get("/{short_code}")
async def redirect_to_original(
    short_code: str,
    request: Request,
    session: Annotated[
        AsyncSession,
        Depends(db_session.session_getter),
    ],
) -> RedirectResponse:
    service = RedirectService.build(session)

    original_url = await service.execute(
        short_code=short_code,
        ip_address=(
            request.headers.get("X-Real-IP")
            or request.headers.get("X-Forwarded-For", "").split(",")[0].strip()
            or (request.client.host if request.client else None)
        ),
        user_agent=request.headers.get("user-agent"),
    )

    if original_url is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Link not found or expired",
        )

    return RedirectResponse(
        url=original_url,
        status_code=status.HTTP_302_FOUND,
    )
