import asyncio
from sqlmodel import Session, create_engine
from sqlalchemy.ext.asyncio import create_async_engine
from settings import settings
from fastapi import FastAPI
from fastapi.routing import APIRoute
from fastapi.routing import APIWebSocketRoute
from fastapi import HTTPException
import json
import redis
from loguru import logger
from models import *

engine = create_engine(
    str(settings.PG_URL),
    echo=False,
    # connect_args={"options": "-c timezone=Asia/Shanghai"},
)
async_engine = create_async_engine(
    str(settings.ASYNC_PG_URL),
    echo=False,
    # connect_args={"options": "-c timezone=Asia/Shanghai"},
)


async def check_rate_limit(key: str, max_attempts: int = 5, window: int = 60) -> None:
    """基于 Redis 的滑动窗口频率限制
    key: 标识（如 IP 或用户名）
    max_attempts: 窗口内最大尝试次数
    window: 时间窗口（秒）
    超过限制则抛出 HTTPException 429
    """
    now = asyncio.get_event_loop().time()
    pipe = redisclient.pipeline()
    window_key = f"ratelimit:{key}"
    await pipe.zadd(window_key, {str(now): now})
    await pipe.zremrangebyscore(window_key, 0, now - window)
    await pipe.zcard(window_key)
    await pipe.expire(window_key, window)
    results = await pipe.execute()
    count = results[2]
    if count > max_attempts:
        raise HTTPException(
            status_code=429,
            detail="请求过于频繁，请稍后再试",
        )


datas = json.load(open("media/initial.json", "r", encoding="utf-8"))

redisclient = redis.asyncio.Redis(
    username=settings.REDIS_USERNAME,
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    password=settings.REDIS_PASSWORD,
    db=settings.REDIS_DB,
)


def init_db(app: FastAPI):
    from sqlmodel import SQLModel, select, update

    # await redisclient.flushdb()
    # Need imported all models in project for create tables

    from src.user import create_user

    with Session(engine) as db:
        SQLModel.metadata.create_all(engine)
        route_id = []
        user_route_id = []
        user_route_exclude = {
            "/api/user/": ["POST", "DELETE", "PATCH", "GET"],
            "/api/interface/": ["POST", "DELETE", "PATCH", "GET"],
            "/api/menu/": ["POST", "DELETE", "PATCH", "GET"],
            "/api/dept/": ["POST", "DELETE", "PATCH", "GET"],
            "/api/role/": ["POST", "DELETE", "PATCH", "GET"],
        }

        def include(path):
            for k, v in user_route_exclude.items():
                if path.startswith(k):
                    for method in v:
                        return False
            return True

        # 初始化接口
        for route in app.routes:
            if isinstance(route, APIRoute):
                for method in route.methods:
                    if method == "OPTIONS":
                        continue
                    interface = db.exec(
                        select(Interface)
                        .where(Interface.path == route.path)
                        .where(Interface.method == method)
                    ).first()

                    if not interface:
                        interface = Interface(
                            name=route.name, path=route.path, method=method
                        )
                        db.add(interface)
                        db.commit()
                        db.refresh(interface)
                        logger.info(f"初始化接口: {route.path} {method}")
                    if include(interface.path):
                        user_route_id.append(interface.id)
                    route_id.append(interface.id)
            elif isinstance(route, APIWebSocketRoute):
                interface = db.exec(
                    select(Interface)
                    .where(Interface.path == route.path)
                    .where(Interface.method == "websocket")
                ).first()

                if not interface:
                    interface = Interface(
                        name=route.name, path=route.path, method="websocket"
                    )
                    db.add(interface)
                    db.commit()
                    db.refresh(interface)
                    logger.info(f"初始化接口: {route.path} websocket")
                if include(interface.path):
                    user_route_id.append(interface.id)
                route_id.append(interface.id)

        # 初始化角色
        role = db.exec(select(Role).where(Role.name == "Admin")).first()
        if not role:
            role = Role(name="Admin", permission=2, interfaces=route_id)
            db.add(role)
            db.commit()
            db.refresh(role)
            logger.info("初始化角色: Admin")
        else:
            role.interfaces = route_id
            db.commit()
            db.refresh(role)
        user_role = db.exec(select(Role).where(Role.name == "User")).first()
        if not user_role:  # 用户角色:比如微信用户
            user_role = Role(name="User", permission=4, interfaces=user_route_id)
            db.add(user_role)
            db.commit()
            db.refresh(user_role)
            logger.info("初始化角色: User")

        db.add(role)
        db.commit()
        db.refresh(role)

        # 初始化部门
        dept = db.exec(select(Dept).where(Dept.name == "Admin")).first()
        if not dept:
            dept = Dept(name="Admin", key="admin")
            db.add(dept)
            db.commit()
            db.refresh(dept)
            logger.info("初始化部门: Admin")

        # 初始化用户
        user = db.exec(
            select(User).where(User.email == settings.FIRST_SUPERUSER)
        ).first()
        if not user:
            user = create_user(
                db=db,
                user_in=UserCreate(
                    fullname="admin",
                    email=settings.FIRST_SUPERUSER,
                    password=settings.FIRST_SUPERUSER_PASSWORD,
                    is_superuser=True,
                    dept_id=dept.id,
                    roles=[role.id],
                    avatar="/h.jpeg",
                ),
            )
            user.is_active = True
            db.add(user)
            db.commit()
            db.refresh(user)
            logger.info(f"初始化用户: {user.email}")

        for i in datas["menus"]:
            if m := db.exec(select(Menu).where(Menu.name == i["name"])).first():
                continue
            m = Menu(**i)
            db.add(m)
            logger.info(f"初始化菜单: {i['label']}")
        db.commit()

        # 初始化 AI 模型
        seed_models = []
        for m_cfg in seed_models:
            if db.exec(select(Model).where(Model.name == m_cfg["name"])).first():
                continue
            db.add(Model(**m_cfg))
            logger.info(f"初始化模型: {m_cfg['label']}")
        db.commit()
