from typing import Annotated, Self
from pydantic import (
    AnyUrl,
    PostgresDsn,
    computed_field,
    BeforeValidator,
    EmailStr,
    model_validator,
)
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic_core import MultiHostUrl
import secrets
import os


def parse_origins(origins: str | list[AnyUrl]) -> list[AnyUrl] | str:
    if isinstance(origins, str) and not origins.startswith("["):
        return [AnyUrl(i) for i in origins.split(",")]
    elif isinstance(origins, str) and origins.startswith("["):
        return [AnyUrl(i) for i in origins[1:-1].split(",")]
    else:
        raise ValueError(origins)


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=r".env", env_ignore_empty=True, extra="ignore"
    )  # 优先级高,没法有默认值
    PROJECT_NAME: str
    API: str
    ALLOW_HOSTS: list[str] = []
    ORIGINS: Annotated[list[AnyUrl] | str, BeforeValidator(parse_origins)] = [
        "http://localhost:3000",
        "http://localhost:5173",
    ]

    @computed_field
    @property
    def ALL_ALLOWED_ORIGINS(self) -> list[str]:
        return [str(i).rstrip("/") for i in self.ORIGINS]

    IS_PRODUCTION: bool = False
    SECRET_KEY: str = secrets.token_urlsafe(32)
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 600
    ACTIVATE_TOKEN_EXPIRE_MINUTES: int = 5
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    RESET_TOKEN_EXPIRE_MINUTES: int = 5

    BACK_HOST: str = "0.0.0.0"
    BACK_PORT: int = 8080

    PG_HOST: str = "localhost"
    PG_PORT: int = 5432
    PG_DATABASE: str
    PG_USER: str = "postgres"
    PG_PASSWORD: str

    @computed_field  # type: ignore[prop-decorator]
    @property
    def PG_URL(self) -> PostgresDsn:
        return MultiHostUrl.build(
            scheme="postgresql+psycopg2",
            username=self.PG_USER,
            password=self.PG_PASSWORD,
            host=self.PG_HOST,
            port=self.PG_PORT,
            path=self.PG_DATABASE,
        )

    @computed_field  # type: ignore[prop-decorator]
    @property
    def ASYNC_PG_URL(self) -> PostgresDsn:
        return MultiHostUrl.build(
            scheme="postgresql+asyncpg",
            username=self.PG_USER,
            password=self.PG_PASSWORD,
            host=self.PG_HOST,
            port=self.PG_PORT,
            path=self.PG_DATABASE,
        )

    CACHE_BACKEND: str = "memory"

    REDIS_HOST: str = "localhost"
    REDIS_USERNAME: str = "default"
    REDIS_PORT: int = 6379
    REDIS_PASSWORD: str = "123456"
    REDIS_DB: int = 1

    SERVER_HOST: str = "192.168.1.102:8090"

    SMTP_SSL: bool = False
    SMTP_PORT: int = 587
    SMTP_HOST: str | None = None
    SMTP_USER: str | None = None
    SMTP_PASSWORD: str | None = None
    # TODO: update type to EmailStr when sqlmodel supports it
    EMAILS_FROM_EMAIL: str | None = None
    EMAILS_FROM_NAME: str | None = None

    @model_validator(mode="after")
    def _validate_secret_key(self) -> Self:
        if self.IS_PRODUCTION:
            # 生产环境必须通过环境变量设置 SECRET_KEY，禁止使用默认随机值
            import os

            if not os.environ.get("SECRET_KEY"):
                raise ValueError(
                    "生产环境必须通过环境变量 SECRET_KEY 设置密钥，不能使用默认值"
                )
        if len(self.SECRET_KEY) < 32:
            raise ValueError("SECRET_KEY 长度至少 32 个字符")
        return self

    @model_validator(mode="after")
    def _set_default_emails_from(self) -> Self:
        if not self.EMAILS_FROM_NAME:
            self.EMAILS_FROM_NAME = self.PROJECT_NAME
        return self

    @computed_field  # type: ignore[prop-decorator]
    @property
    def emails_enabled(self) -> bool:
        return bool(self.SMTP_HOST and self.EMAILS_FROM_EMAIL)

    FIRST_SUPERUSER: str
    FIRST_SUPERUSER_PASSWORD: str

    # MEDIA_PATH: str = "./media/"
    MEDIA_PATH: str = os.path.join(os.path.dirname(__file__), "media")


settings = Settings()
