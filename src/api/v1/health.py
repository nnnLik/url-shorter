from fastapi import APIRouter, status
from fastapi.responses import JSONResponse
from sqlalchemy import text

from core.database import db_session
from core.rabbitmq import rabbitmq_client
from core.redis import redis_client

router = APIRouter(
    prefix='/health',
    tags=['health'],
)


@router.get('')
async def health_check() -> JSONResponse:
    return JSONResponse(
        content={'status': 'ok'},
        status_code=status.HTTP_200_OK,
    )


@router.get('/ready')
async def readiness_check() -> JSONResponse:
    checks = {
        'database': False,
        'redis': False,
        'rabbitmq': False,
    }

    async with db_session._session_factory() as session:
        await session.execute(text('SELECT 1'))
        checks['database'] = True

    await redis_client._client.ping()
    checks['redis'] = True

    connection = rabbitmq_client.get_connection()
    if connection and not connection.is_closed:
        checks['rabbitmq'] = True

    all_ready = all(checks.values())

    return JSONResponse(
        content={
            'status': 'ready' if all_ready else 'not ready',
            'checks': checks,
        },
        status_code=status.HTTP_200_OK if all_ready else status.HTTP_503_SERVICE_UNAVAILABLE,
    )
