from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from settings import settings


def init(app: FastAPI):
    if settings.ALL_ALLOWED_ORIGINS:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=settings.ALL_ALLOWED_ORIGINS,
            allow_credentials=True,
        )
    app.add_middleware(
        TrustedHostMiddleware, allowed_hosts=settings.ALLOW_HOSTS
    )  # 只允许指定列表中的 Host 头，防止 Host header 注入
