from pathlib import Path
from typing import Annotated, Optional
from fastapi import Form, HTTPException
from pydantic import EmailStr, model_validator
from sqlmodel import (
    Field,
    Relationship,
    SQLModel,
    Column,
    JSON,
)
from enum import Enum
from sqlalchemy import event, Integer, DateTime
import datetime
from sqlalchemy.sql import func
from settings import settings
import os
from pydantic import field_serializer
from loguru import logger

# 不要引入utils的模块，否则会导致循环导入


class BaseModel(SQLModel):
    id: Optional[int] = Field(default=None, primary_key=True)
    creator_id: Optional[int] = Field(default=None, nullable=True)
    dept_id: Optional[int] = Field(default=None, nullable=True)
    created_at: datetime.datetime = Field(
        default=None,  # 应用层默认值
        sa_type=DateTime,
        sa_column_kwargs={"server_default": func.now()},  # 数据库默认值
        nullable=True,
    )
    updated_at: datetime.datetime = Field(
        default=None,  # 允许为 None，这样 Pydantic 不会抛出缺失错误
        sa_type=DateTime,
        sa_column_kwargs={
            "server_default": func.now(),  # 数据库默认值
            "onupdate": func.now(),  # 更新时自动更新
        },
    )

    @field_serializer("created_at", "updated_at")
    def serialize_datetime(self, dt: datetime) -> str | None:
        if dt is None:
            return None
        if dt.tzinfo is None:
            return dt.strftime("%Y-%m-%d %H:%M:%S")
        return dt.astimezone().strftime("%Y-%m-%d %H:%M:%S")


class LoginLog(BaseModel, table=True):
    user_id: int
    username: str
    ip: str
    user_agent: str


class File(BaseModel, table=True):
    name: str
    url: str
    size: int
    type: str


# 在删除前执行自定义操作
@event.listens_for(File, "before_delete")
def before_delete(mapper, connection, target):
    file_path = Path(os.path.join(settings.MEDIA_PATH, target.url))
    logger.info(f"删除文件: {target.url}")
    if file_path.exists():
        file_path.unlink()  # 删除文件


class Button(BaseModel, table=True):
    name: str
    code: str
    menu_id: int | None = Field(default=None, nullable=True)


class Interface(BaseModel, table=True):
    name: str
    method: str
    path: str


class Menu(BaseModel, table=True):
    label: str
    name: str
    icon: str
    path: str
    component: str
    sort: int = 0
    is_link: bool = False
    is_catalog: bool = False
    parent_id: int | None = Field(default=None, nullable=True)


class PermissionChoice(Enum):
    me = 1  # 自己
    dept = 2  # 部门
    dept_and_sub = 3  # 部门及其子部门
    all = 4  # 没有部门限制


class Role(BaseModel, table=True):
    name: str
    permission: int = Field(
        default=1,
        sa_column=Column(Integer),  # 使用枚举的数字值  # 存储为整数
    )
    interfaces: list[int] = Field(default_factory=list, sa_column=Column(JSON))
    menus: list[int] = Field(default_factory=list, sa_column=Column(JSON))
    buttons: list[int] = Field(default_factory=list, sa_column=Column(JSON))


class Dept(BaseModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str
    key: str | None
    users: list["User"] = Relationship(back_populates="dept")
    parent_id: Optional[int] = Field(default=None, foreign_key="dept.id", nullable=True)

    children: list["Dept"] = Relationship(
        back_populates="parent",
        sa_relationship_kwargs={"foreign_keys": "Dept.parent_id", "lazy": "dynamic"},
    )

    parent: "Dept" = Relationship(
        back_populates="children",
        sa_relationship_kwargs={
            "remote_side": "Dept.id",
            "foreign_keys": "Dept.parent_id",
        },
    )


class DeptPublic(BaseModel):
    name: str
    key: str | None
    parent_id: Optional[int] = Field(default=None, foreign_key="dept.id", nullable=True)
    parent__name: str | None = Field(default=None, nullable=True)
    parent__key: str | None = Field(default=None, nullable=True)


class DeptsPublic(SQLModel):
    data: list[DeptPublic]  # type: ignore
    total: int


class TokenPayload(SQLModel):
    sub: str | None = None


class Token(SQLModel):
    token: str
    token_type: str = "bearer"


class Item(BaseModel, table=True):
    name: str
    description: str


class UserBase(SQLModel):
    id: int | None = Field(default=None, primary_key=True)
    weixin_id: Optional[str] = Field(default=None, max_length=255)
    email: Optional[EmailStr] = Field(
        default=None, index=True, unique=True, max_length=255
    )
    is_active: bool = False
    is_superuser: bool = False
    fullname: str | None = Field(default=None, max_length=255)
    avatar: str | None = Field(default=None, max_length=255)


def validate_password_strength(password: str) -> str:
    if len(password) < 8:
        raise HTTPException(status_code=400, detail="密码长度至少8位")
    if not any(c.isalpha() for c in password):
        raise HTTPException(status_code=400, detail="密码必须包含至少一个字母")
    if not any(c.isdigit() for c in password):
        raise HTTPException(status_code=400, detail="密码必须包含至少一个数字")
    return password


class UserRegist(SQLModel):
    email: EmailStr
    password: str
    fullname: str | None = Annotated[str, Form()]

    @model_validator(mode="after")
    def check_password(self):
        validate_password_strength(self.password)
        return self

    @classmethod
    def as_form(
        cls,
        email: str = Form(...),
        password: str = Form(...),
        fullname: str = Form(...),
    ) -> "UserRegist":
        return cls(fullname=fullname, email=email, password=password)


class UserResetEmail(SQLModel):
    email: EmailStr

    @classmethod
    def as_form(cls, email: EmailStr = Form(...)) -> "UserResetEmail":
        return cls(email=email)


class UserReset(SQLModel):
    password: str
    password_confirm: str

    @model_validator(mode="after")
    def check_password(self):
        if self.password != self.password_confirm:
            raise HTTPException(status_code=400, detail="两次密码不一致")
        validate_password_strength(self.password)
        return self

    @classmethod
    def as_form(
        cls,
        password: str = Form(...),
        password_confirm: str = Form(...),
    ) -> "UserReset":
        return cls(password=password, password_confirm=password_confirm)


class UserChangePassword(SQLModel):
    old_password: str
    new_password: str
    new_password_confirm: str

    @model_validator(mode="after")
    def check_password(self):
        if self.new_password != self.new_password_confirm:
            raise HTTPException(status_code=400, detail="两次密码不一致")
        validate_password_strength(self.new_password)
        return self

    @classmethod
    def as_form(
        cls,
        old_password: str = Form(...),
        new_password: str = Form(...),
        new_password_confirm: str = Form(...),
    ) -> "UserChangePassword":
        return cls(
            old_password=old_password,
            new_password=new_password,
            new_password_confirm=new_password_confirm,
        )


class UserCreate(UserBase):
    password: str
    dept_id: int | None = Field(default=None)
    roles: list[int] = Field(default_factory=list, sa_column=Column(JSON))


class UserUpdate(UserBase):
    password: str | None = Field(default=None, min_length=8, max_length=40)
    email: EmailStr | None = Field(default=None, max_length=255)
    dept_id: int | None = Field(default=None)
    roles: list[int] = Field(default_factory=list, sa_column=Column(JSON))


class UserPublic(UserBase):
    id: int
    dept_id: int | None = Field(default=None)
    dept__name: str | None = Field(default=None)
    roles: list[int] = Field(default_factory=list, sa_column=Column(JSON))
    created_at: datetime.datetime | None = Field(
        default=None,
        sa_type=DateTime,
    )
    updated_at: datetime.datetime | None = Field(
        default=None,
        sa_type=DateTime,
    )

    @field_serializer("created_at", "updated_at")
    def serialize_datetime(self, dt: datetime) -> str | None:
        if dt is None:
            return None
        if dt.tzinfo is None:
            return dt.strftime("%Y-%m-%d %H:%M:%S")
        return dt.astimezone().strftime("%Y-%m-%d %H:%M:%S")


class UsersPublic(SQLModel):
    data: list[UserPublic]
    total: int


class Chat(BaseModel, table=True):
    model: str = ""
    name: str = ""
    messages: list[dict] = Field(default_factory=list, sa_column=Column(JSON))
    role_id: int | None = Field(default=None)
    tokens_used: int = 0
    last_message_at: datetime.datetime | None = Field(default=None, sa_type=DateTime)


class Model(BaseModel, table=True):
    name: str
    label: str
    type: str = "openai"
    base_url: str = ""
    api_key: str = ""
    vision: bool = False
    tools: bool = False
    extra: dict = Field(default_factory=dict, sa_column=Column(JSON))


class User(UserBase, BaseModel, table=True):
    roles: list[int] = Field(default_factory=list, sa_column=Column(JSON))
    dept_id: int | None = Field(foreign_key="dept.id", default=None)
    dept: Dept = Relationship(back_populates="users")
    hash_password: Optional[str] = Field(default=None, max_length=255)
    created_at: datetime.datetime = Field(
        default=None,  # 应用层默认值
        sa_type=DateTime,
        sa_column_kwargs={"server_default": func.now()},  # 数据库默认值
        nullable=True,
    )
    updated_at: datetime.datetime = Field(
        default=None,  # 允许为 None，这样 Pydantic 不会抛出缺失错误
        sa_type=DateTime,
        sa_column_kwargs={
            "server_default": func.now(),  # 数据库默认值
            "onupdate": func.now(),  # 更新时自动更新
        },
    )

    @model_validator(mode="after")
    def validate_credentials(self):
        if self.weixin_id is None:
            if self.email is None or self.hash_password is None:
                raise ValueError(
                    "When weixin_id is empty, both email and hash_password are required"
                )
        return self
