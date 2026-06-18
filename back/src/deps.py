import jwt
import re
import security
from typing import Annotated
from fastapi import Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordBearer
from pydantic import ValidationError
from sqlmodel import Session, select
from db import engine, async_engine
from settings import settings
from models import User, Role, Interface, Dept, PermissionChoice
from security import TokenType, TokenPayload
from sqlmodel.ext.asyncio.session import AsyncSession

# from main import producer
bearer_oauth2 = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API}/login/access", auto_error=False
)
cookie_oauth2 = security.OAuth2WithCookie(cookie_name="access_token")
cookie_oauth2_refresh = security.OAuth2WithCookie(cookie_name="refresh_token")


def get_db():
    with Session(engine) as session:
        yield session


async def get_async_db():
    async with AsyncSession(async_engine) as db:
        yield db


DB = Annotated[Session, Depends(get_db)]  # 获取数据库连接session
ASYNC_DB = Annotated[AsyncSession, Depends(get_async_db)]  # 获取数据库连接session
BearerToken = Annotated[str, Depends(bearer_oauth2)]
CookieToken = Annotated[str, Depends(cookie_oauth2)]


BearerTokenRefresh = Annotated[str, Depends(bearer_oauth2)]
CookieTokenRefresh = Annotated[str, Depends(cookie_oauth2_refresh)]


def parse_token(
    token: str, token_type: TokenType, raise_error=True
) -> TokenPayload | None:
    """解析token"""
    if not token:
        if raise_error:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="无效的认证凭据",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return None
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[security.ALGORITHM]
        )
        if payload.get("type") != token_type.value:
            if raise_error:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="无效的token类型",
                )
            return None
        token_data = TokenPayload(**payload)
    except ValidationError:
        if raise_error:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="无法验证凭据",
            )
        return None
    except jwt.ExpiredSignatureError:
        if raise_error:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="登录已过期",
            )
        return None
    return token_data


async def activate_user(db: ASYNC_DB, token: str) -> User:
    token_data = parse_token(token, TokenType.activate_token)
    user = (await db.exec(select(User).where(User.id == int(token_data.sub)))).first()
    if not user:
        raise HTTPException(status_code=404, detail="账号未找到")
    return user


async def reset_user(db: ASYNC_DB, token: str) -> User:
    token_data = parse_token(token, TokenType.reset_token)
    user = (await db.exec(select(User).where(User.id == int(token_data.sub)))).first()
    if not user:
        raise HTTPException(status_code=404, detail="账号未找到")
    if not user.is_active:
        raise HTTPException(status_code=400, detail="账号未激活")

    return user


async def refresh_user(
    db: ASYNC_DB, token_bearer: BearerTokenRefresh, token_cookie: CookieTokenRefresh
) -> User:
    token = token_bearer if token_bearer else token_cookie
    token_data = parse_token(token, TokenType.refresh_token)
    user = (await db.exec(select(User).where(User.id == int(token_data.sub)))).first()
    if not user:
        raise HTTPException(status_code=404, detail="账号未找到")
    if not user.is_active:
        raise HTTPException(status_code=400, detail="账号未激活")
    return user


async def current_user(
    db: ASYNC_DB, token_bearer: BearerToken, token_cookie: CookieToken
) -> User:
    token = token_bearer if token_bearer else token_cookie
    token_data = parse_token(token, TokenType.access_token)
    user = (await db.exec(select(User).where(User.id == int(token_data.sub)))).first()
    if not user:
        raise HTTPException(status_code=404, detail="账号未找到")
    if not user.is_active:
        raise HTTPException(status_code=400, detail="账号未激活")
    return user


async def current_user_id(
    db: ASYNC_DB, token_bearer: BearerToken, token_cookie: CookieToken
) -> int | None:
    token = token_bearer if token_bearer else token_cookie
    token_data = parse_token(token, TokenType.access_token, raise_error=False)
    if not token_data:
        return None
    user = (await db.exec(select(User).where(User.id == int(token_data.sub)))).first()
    if not user:
        return None
    return user.id


# 根据token获取对应用户
ActivateUser = Annotated[User, Depends(activate_user)]
ResetUser = Annotated[User, Depends(reset_user)]
RefreshUser = Annotated[User, Depends(refresh_user)]
CurrentUser = Annotated[User, Depends(current_user)]
CurrentUserId = Annotated[int | None, Depends(current_user_id)]


async def is_superuser(current_user: CurrentUser) -> User:
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="用户没有足够的权限[超级用户]",
        )
    return current_user


SuperUser = Depends(
    is_superuser
)  # 放在dependencies中，表示需要验证是否为超级用户, 只能只用Depends 不能加注解


async def get_sub_dept(db: ASYNC_DB, dept_id: int | None) -> list[int]:
    if dept_id is None:
        return []
    depts = (await db.exec(select(Dept))).all()
    result = []
    stack = [dept_id]
    while stack:
        parent = stack.pop()
        for dept in depts:
            if dept.parent_id == parent:
                result.append(dept.id)
                stack.append(dept.id)
    return result


async def get_permission(
    db: ASYNC_DB, requset: Request, current_user: CurrentUser
) -> list:
    """获取用户可用部门的数据，以及否有权限访问当前路由"""
    route_permission = False
    user_depts = []

    if current_user.is_superuser:
        route_permission = True
        user_depts.append(None)
    roles = current_user.roles

    interfaces_ids = []
    permissions = []
    for role in roles:
        role = (await db.exec(select(Role).where(Role.id == role))).one()
        permissions.append(role.permission)
        interfaces_ids.extend(role.interfaces)

    interfaces = (
        await db.exec(select(Interface).where(Interface.id.in_(interfaces_ids)))
    ).all()
    for i in interfaces:
        pattern = re.sub(r"{[^}]+}", r"[^/]+", i.path)
        pattern = f"^{pattern}$"  # 添加开头和结尾限制符
        if re.match(pattern, requset.url.path) is not None:
            route_permission = True
    if PermissionChoice.dept.value in permissions:
        user_depts.append(current_user.dept_id)
    elif PermissionChoice.dept_and_sub.value in permissions:
        sub_depts = await get_sub_dept(db, current_user.dept_id)
        user_depts.extend(sub_depts + [current_user.dept_id])
    elif PermissionChoice.all.value in permissions:
        user_depts.append(None)
    if not route_permission:
        raise HTTPException(
            status_code=403,
            detail="用户没有足够的权限[权限不足]",
        )
    return user_depts


Permission = Annotated[
    list[int], Depends(get_permission)
]  # 获取用户可用部门的数据，以及否有权限访问当前路由


def get_client(request: Request) -> dict:
    """获取客户端信息"""
    client_ip = request.client.host
    user_agent = request.headers.get("user-agent", "unknown")
    return {
        "ip": client_ip,
        "user_agent": user_agent,
        "path": request.url.path,
        "query": dict(request.query_params),
    }


Client = Annotated[dict, Depends(get_client)]  # 有返回值就要定义类型注解
