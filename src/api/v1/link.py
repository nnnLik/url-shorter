from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import db_session
from dtos import BatchCreateLinkRequestDTO, BatchCreateLinkResponseDTO, CreateLinkRequestDTO, CreateLinkResponseDTO
from services import BatchCreateLinkService, CreateLinkService, RedirectService

router = APIRouter(
    prefix='/links',
    tags=['links'],
)


@router.post('/pack', status_code=status.HTTP_201_CREATED)
async def create_link(
    create_link_request_dto: CreateLinkRequestDTO,
    session: Annotated[AsyncSession, Depends(db_session.session_getter)],
) -> CreateLinkResponseDTO:
    service = CreateLinkService.build(session)

    try:
        return await service.execute(
            original_url=create_link_request_dto.original_url,
            expires_at=create_link_request_dto.expires_at,
        )
    except CreateLinkService.CreateLinkServiceError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)) from e


@router.post('/batch', status_code=status.HTTP_201_CREATED)
async def batch_create_links(
    batch_create_link_request_dto: BatchCreateLinkRequestDTO,
    session: Annotated[AsyncSession, Depends(db_session.session_getter)],
) -> BatchCreateLinkResponseDTO:
    service = BatchCreateLinkService.build(session)

    try:
        return await service.execute(
            original_url=batch_create_link_request_dto.original_url,
            count=batch_create_link_request_dto.count,
            expires_at=batch_create_link_request_dto.expires_at,
        )
    except BatchCreateLinkService.BatchCreateLinkServiceError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)) from e


@router.get('/unpack/{short_code}')
async def redirect_to_original(
    short_code: str,
    request: Request,
    session: Annotated[
        AsyncSession,
        Depends(db_session.session_getter),
    ],
) -> RedirectResponse:
    service = RedirectService.build(session)

    try:
        original_url = await service.execute(
            short_code=short_code,
            ip_address=(
                request.headers.get('X-Real-IP')
                or request.headers.get('X-Forwarded-For', '').split(',')[0].strip()
                or (request.client.host if request.client else None)
            ),
            user_agent=request.headers.get('user-agent'),
        )

        return RedirectResponse(
            url=original_url,
            status_code=status.HTTP_302_FOUND,
        )
    except RedirectService.LinkNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Link not found or expired',
        ) from e
