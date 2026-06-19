import datetime
import os
from fastapi import APIRouter, Cookie, Depends, Form, HTTPException, Response, Request
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.templating import Jinja2Templates
from typing import Annotated, Any, Optional
from src.user import authenticate
from models import (
    User,
    UserChangePassword,
    UserReset,
    UserPublic,
    UserRegist,
    UserResetEmail,
    LoginLog,
)
from settings import settings
from utils import send_reset_email, send_activate_email
from .deps import DB, CurrentUser, RefreshUser, ActivateUser, ResetUser, ASYNC_DB
from security import hash_password, create_token, TokenType
from .user import get_user
from db import redisclient, check_rate_limit

router = APIRouter()
templates = Jinja2Templates(directory=os.path.join(settings.MEDIA_PATH, "templates"))


async def login(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


router.add_api_route("/", endpoint=login, methods=["GET", "POST"], name="后端登陆页")


@router.get("/register", name="后端注册页")
async def login(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})


@router.post("/signup", response_model=UserPublic, name="注册")
async def signup(
    db: ASYNC_DB, request: Request, user_in: UserRegist = Depends(UserRegist.as_form)
) -> Any:
    """
    注册用户
    """
    # 限流：按 IP 限制注册频率
    client_ip = request.client.host if request.client else "unknown"
    await check_rate_limit(f"signup:ip:{client_ip}", max_attempts=3, window=60)

    user = await get_user(db, user_in.email)
    if user:
        if user.is_active:
            raise HTTPException(status_code=403, detail="邮箱已注册")
        else:
            raise HTTPException(
                status_code=400,
                detail="邮箱已注册，但未激活，请先激活邮箱",
            )
    user = User(
        email=user_in.email,
        fullname=user_in.fullname,
        hash_password=hash_password(user_in.password),
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)

    activate_token = create_token(
        user.id,
        datetime.timedelta(minutes=settings.ACTIVATE_TOKEN_EXPIRE_MINUTES),
        TokenType.activate_token.value,
    )

    success = send_activate_email(
        to_email=user_in.email,
        user_name=user_in.fullname,
        activate_link=f"{settings.SERVER_HOST}/api/login/activate?token={activate_token}",
        expiration_time=f"{settings.ACTIVATE_TOKEN_EXPIRE_MINUTES}分钟",
    )
    if not success:
        await db.delete(user)
        await db.commit()
        raise HTTPException(status_code=500, detail="邮件发送失败")
    return templates.TemplateResponse("signup_success.html", {"request": request})


@router.get("/reset", name="后端重置密码页")
async def reset_password(request: Request):
    return templates.TemplateResponse("reset.html", {"request": request})


@router.post("/reset", name="重置密码邮件发送")
async def reset_password(db: ASYNC_DB, request: Request, user: UserResetEmail):
    # 限流：按 IP 限制密码重置频率
    client_ip = request.client.host if request.client else "unknown"
    await check_rate_limit(f"reset:ip:{client_ip}", max_attempts=3, window=60)
    
    user_obj = await get_user(db, email=user.email)
    if not user_obj:
        raise HTTPException(status_code=400, detail="邮箱不存在")
    elif not user_obj.is_active:
        raise HTTPException(status_code=400, detail="邮箱未激活")
    else:
        reset_token = create_token(
            user_obj.id,
            datetime.timedelta(minutes=settings.RESET_TOKEN_EXPIRE_MINUTES),
            TokenType.reset_token.value,
        )
        send_reset_email(
            user_obj.email,
            user_obj.fullname,
            f"http://localhost:8000/api/login/reset_input?token={reset_token}",
            f"{settings.RESET_TOKEN_EXPIRE_MINUTES}分钟",
        )
        return {"success": True}


@router.get("/reset_success", name="后端重置密码成功页")
async def reset_success(request: Request):
    return templates.TemplateResponse("reset_success.html", {"request": request})


@router.get("/reset_input", name="后端重置密码输入页")
async def reset_password(request: Request, token: str):
    return templates.TemplateResponse(
        "reset_input.html", {"request": request, "token": token}
    )


@router.post("/reset_input", name="重置密码")
async def reset_password(
    db: ASYNC_DB,
    request: Request,
    user_reset: ResetUser,
    user_in: UserReset = Depends(UserReset.as_form),
):
    user = await get_user(db, user_reset.email)
    user.hash_password = hash_password(user_in.password)
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return templates.TemplateResponse("reset_success.html", {"request": request})


@router.get("/change_password", name="后端修改密码页")
async def change_password(request: Request, current_user: CurrentUser):
    return templates.TemplateResponse("change_password.html", {"request": request})


@router.post("/change_password", name="修改密码")
async def change_password(
    db: ASYNC_DB, current_user: CurrentUser, user_in: UserChangePassword
):
    current_user.hash_password = hash_password(user_in.new_password)
    db.add(current_user)
    await db.commit()
    await db.refresh(current_user)
    return {"success": True}


@router.get("/change_password_success", name="后端修改密码成功页")
async def reset_success(request: Request):
    return templates.TemplateResponse("reset_success.html", {"request": request})


@router.get("/activate", name="activate")
async def activate(request: Request, user: ActivateUser, db: ASYNC_DB):
    user.is_active = True
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return templates.TemplateResponse("activate_success.html", {"request": request})


@router.post("/access/", name="登陆")
async def access_token(
    db: ASYNC_DB,
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    request: Request,
    response: Response,
    captcha: Annotated[str, Form()],
    remember_me: Annotated[bool, Form()] = False,
    session_id_cookie: Optional[str] = Cookie(None),
    session_id_form: Annotated[str, Form()] = None,
) -> dict[str, str]:
    # 频率限制：按 IP 和用户名分别限制
    client_ip = request.client.host if request.client else "unknown"
    await check_rate_limit(f"login:ip:{client_ip}", max_attempts=10, window=60)
    await check_rate_limit(f"login:user:{form_data.username}", max_attempts=5, window=60)

    if not session_id_cookie and not session_id_form:
        raise HTTPException(
            status_code=401,
            detail="请求错误",
            headers={"WWW-Authenticate": "Bearer"},
        )
    session_id = session_id_cookie if session_id_cookie else session_id_form
    captcha_cache = await redisclient.get(session_id)
    captcha_cache = captcha_cache.decode("utf-8") if captcha_cache else None
    if not captcha_cache:
        raise HTTPException(
            status_code=401,
            detail="验证码已过期",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if captcha.lower() == captcha_cache.lower():
        await redisclient.delete(session_id)
    else:
        raise HTTPException(
            status_code=401,
            detail="验证码错误",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = await authenticate(
        db=db, email=form_data.username, password=form_data.password
    )
    if not user:
        raise HTTPException(
            status_code=401,
            detail="用户名或密码错误",
            headers={"WWW-Authenticate": "Bearer"},
        )
    elif not user.is_active:
        raise HTTPException(
            status_code=401,
            detail="账号未激活",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # 生产环境开启 secure cookie（需要 HTTPS）
    cookie_secure = settings.IS_PRODUCTION

    # 生成 Access Token
    access_token = create_token(
        user.id,
        datetime.timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
        TokenType.access_token.value,
    )

    # 生成 Refresh Token
    refresh_token = create_token(
        user.id,
        datetime.timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
        TokenType.refresh_token.value,
    )
    if remember_me:
        # 设置 Cookie
        response.set_cookie(
            key="access_token",
            value=access_token,
            httponly=True,  #
            secure=cookie_secure,
            samesite="lax",
            expires=datetime.datetime.now(datetime.timezone.utc)
            + datetime.timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
        )
        response.set_cookie(
            key="refresh_token",
            value=refresh_token,
            httponly=True,
            secure=cookie_secure,
            samesite="lax",
            expires=datetime.datetime.now(datetime.timezone.utc)
            + datetime.timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
        )
    else:
        response.set_cookie(
            key="access_token",
            value=access_token,
            httponly=True,  #
            secure=cookie_secure,
            samesite="lax",
            max_age=datetime.timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
        )
        response.set_cookie(
            key="refresh_token",
            value=refresh_token,
            httponly=True,
            secure=cookie_secure,
            samesite="lax",
            max_age=datetime.timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
        )
    lg = LoginLog(
        user_id=user.id,
        username=user.email,
        ip=request.client.host,
        user_agent=request.headers.get("User-Agent"),
    )
    db.add(lg)
    await db.commit()
    # 返回 Token 数据
    return {"access_token": access_token, "refresh_token": refresh_token}


@router.get("/refresh/", name="刷新登陆")
async def refresh_token(db: ASYNC_DB, response: Response, user: RefreshUser):
    # 生成 Refresh Token
    new_refresh_token = create_token(
        user.id,
        datetime.timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
        TokenType.refresh_token.value,
    )

    # 设置 Cookie
    response.set_cookie(
        key="refresh_token",
        value=new_refresh_token,
        httponly=True,
        secure=settings.IS_PRODUCTION,
        samesite="lax",
        max_age=datetime.timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
    )

    # 返回 Token 数据
    return {"refresh_token": new_refresh_token}


@router.get("/logout/", name="退出登陆")
async def logout(response: Response):
    response.delete_cookie(key="access_token")
    response.delete_cookie(key="refresh_token")
    return {"success": True}
