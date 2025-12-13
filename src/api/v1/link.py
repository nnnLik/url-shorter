from typing import Annotated

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Request,
    Response,
    status,
)
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import db_session
from dtos import BatchCreateLinkRequestDTO, CreateLinkRequestDTO
from services import BatchCreateLinkService, CreateLinkService, RedirectService
from utils.fastapi_utils import MsgSpecJSONResponse, decode_msgspec

router = APIRouter(
    prefix="/links",
    tags=["links"],
)


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_link(
    request: Request,
    session: Annotated[AsyncSession, Depends(db_session.session_getter)],
) -> Response:
    request_dto = await decode_msgspec(request, CreateLinkRequestDTO)
    service = CreateLinkService.build(session)

    try:
        result = await service.execute(
            original_url=request_dto.original_url,
            expires_at=request_dto.expires_at,
        )
        return MsgSpecJSONResponse(content=result, status_code=status.HTTP_201_CREATED)
    except CreateLinkService.CreateLinkServiceError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)) from e


@router.post("/batch", status_code=status.HTTP_201_CREATED)
async def batch_create_links(
    request: Request,
    session: Annotated[AsyncSession, Depends(db_session.session_getter)],
) -> Response:
    request_dto = await decode_msgspec(request, BatchCreateLinkRequestDTO)
    service = BatchCreateLinkService.build(session)

    try:
        result = await service.execute(
            original_url=request_dto.original_url,
            count=request_dto.count,
            expires_at=request_dto.expires_at,
        )
        return MsgSpecJSONResponse(content=result, status_code=status.HTTP_201_CREATED)
    except BatchCreateLinkService.BatchCreateLinkServiceError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)) from e


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
