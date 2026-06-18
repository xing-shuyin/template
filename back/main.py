from pathlib import Path
import os
import sys

current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))
from fastapi.staticfiles import StaticFiles
import uvicorn
import middleware
from fastapi import FastAPI
from settings import settings
from fastapi import APIRouter
from db import init_db
from contextlib import asynccontextmanager
from src.routers import initrouters
from loguru import logger


# 配置Loguru
logger.configure(
    handlers=[
        {
            "sink": "log/main.log",
            "rotation": "10 MB",
            "retention": "7 days",
            "enqueue": True,
            "level": "INFO",
            "format": "[{time:MM/DD/YY HH:mm:ss}] | {level: <8} | {message}",
        },
        {
            "sink": sys.stderr,
            "level": "INFO",
            "format": "<dim>[{time:MM/DD/YY HH:mm:ss}]</dim> | <level>{level: <8}</level> | <cyan>{message}</cyan>",
        },
    ]
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield


app = FastAPI(
    title="BLOG",
    lifespan=lifespan,
    openapi_url="/openapi" if not settings.IS_PRODUCTION else None,
    docs_url="/docs" if not settings.IS_PRODUCTION else None,
)


router = APIRouter(prefix=settings.API, tags=["api"])
app.mount(
    f"/{settings.API.strip('/')}/media/",
    StaticFiles(
        directory=os.path.join(current_dir, "media/"),
        follow_symlink=True,
    ),
    name="media",
)
initrouters(router)
app.include_router(router)
middleware.init(app)


if __name__ == "__main__":
    init_db(app=app)
    uvicorn.run(app, host=settings.BACK_HOST, port=settings.BACK_PORT)
