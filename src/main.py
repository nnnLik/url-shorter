from fastapi import FastAPI

from config import settings
from utils.app_utils import get_and_setup_app

app: FastAPI = get_and_setup_app()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.app.HOST,
        port=settings.app.PORT,
        reload=settings.app.RELOAD,
        workers=settings.app.WORKERS,
    )
