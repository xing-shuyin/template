from sqlmodel import SQLModel, cast, select, func, delete, text
from sqlalchemy.dialects.postgresql import JSONB
from fastapi import APIRouter, HTTPException, FastAPI, Query, Request
from src.deps import Permission, CurrentUser, ASYNC_DB
from models import (
    Item,
    Menu,
    Dept,
    Role,
    Interface,
    Button,
    File,
    User,
    Chat,
    Model,
    DeptsPublic,
    UserPublic,
    UsersPublic,
    LoginLog,
)
from typing import Any, List, Optional
from src import login
from sqlalchemy.orm import aliased
from utils import (
    image,
    get_captcha,
    upload_file,
    upload_files,
    download_file,
    iconify_collections,
    iconify_icons,
)
from src.user import me
from datetime import datetime

key2model = {
    "item": Item,
    "menu": Menu,
    "dept": Dept,
    "role": Role,
    "interface": Interface,
    "button": Button,
    "file": File,
    "user": User,
    "chat": Chat,
    "model": Model,
}


def deal_row(rows: list):
    for row in rows:
        for k, v in row.items():
            if isinstance(v, datetime):
                row[k] = v.strftime("%Y-%m-%d %H:%M:%S")


# ─── 可组合的 builder ───


def build_fields(model, values: list[str] | None) -> list:
    fields_all = model.model_fields.keys()
    names = values if values else fields_all
    return [getattr(model, f) for f in list(set(names))]


def build_sort(model, query_params) -> list:
    sort_val = query_params.get("sort")
    if not sort_val:
        return []
    if sort_val.startswith("-"):
        return [getattr(model, sort_val[1:]).desc()]
    return [getattr(model, sort_val)]


def build_joins(model, model_alias, query_params, joins_map) -> tuple[list, list]:
    """returns (extra_fields, join_conditions)"""
    fields = []
    joins = []
    seen = set()
    for v in query_params.getlist("extra[]"):
        parts = v.split("__")
        if len(parts) != 2:
            continue
        rel, field = parts
        if rel == "parent":
            try:
                fields.append(getattr(model_alias, field).label(v))
                if rel not in seen:
                    seen.add(rel)
                    joins.append([model_alias, model_alias.id == model.parent_id])
            except AttributeError:
                pass
        elif rel in joins_map:
            try:
                fields.append(getattr(joins_map[rel], field).label(v))
                if rel not in seen:
                    seen.add(rel)
                    joins.append(
                        [
                            joins_map[rel],
                            joins_map[rel].id == getattr(model, rel + "_id"),
                        ]
                    )
            except AttributeError:
                pass
    return fields, joins


def build_filters(model, query_params, dialect=None) -> list:
    filters = []
    for key, value in query_params.items():
        if key in ("extra[]", "sort"):
            continue
        if "__" not in key:
            if key in model.model_fields.keys():
                filters.append(getattr(model, key) == value)
            continue
        if key.endswith("__gte"):
            filters.append(getattr(model, key.replace("__gte", "")) >= value)
        elif key.endswith("__gt"):
            filters.append(getattr(model, key.replace("__gt", "")) > value)
        elif key.endswith("__lte"):
            filters.append(getattr(model, key.replace("__lte", "")) <= value)
        elif key.endswith("__lt"):
            filters.append(getattr(model, key.replace("__lt", "")) < value)
        elif key.endswith("__in"):
            filters.append(getattr(model, key.replace("__in", "")).in_(value))
        elif key.endswith("__contains"):
            filters.append(
                getattr(model, key.replace("__contains", "")).like(f"%{value}%")
            )
        elif key.endswith("__like"):
            filters.append(getattr(model, key.replace("__like", "")).like(f"%{value}%"))
        elif key.endswith("__startswith"):
            filters.append(
                getattr(model, key.replace("__startswith", "")).like(f"{value}%")
            )
        elif key.endswith("__endswith"):
            filters.append(
                getattr(model, key.replace("__endswith", "")).like(f"%{value}")
            )
        elif key.endswith("__list_contains"):
            col = getattr(model, key.replace("__list_contains", ""))
            if dialect == "sqlite":
                filters.append(
                    text(
                        f"EXISTS (SELECT 1 FROM json_each({model.__tablename__}.{col.name}) WHERE value = :v)"
                    ).bindparams(v=value)
                )
            else:
                filters.append(func.jsonb_exists(cast(col, JSONB), value))
        elif key.endswith("__json_extract__like[]"):
            if dialect == "sqlite":
                raise HTTPException(
                    400, detail="SQLite does not support JSON functions"
                )
            vals = query_params.getlist(key)
            filters.append(
                func.json_extract(
                    getattr(model, key.replace("__json_extract__like[]", "")), vals[0]
                ).like(vals[1] if len(vals) > 1 else "%")
            )
    return filters


def initrouter(model: SQLModel, router: APIRouter | FastAPI, cache_list=None) -> None:
    r = APIRouter()
    model_name = model.__table__.name.lower()
    model_alias = aliased(model)

    if model_name == "dept":
        models = DeptsPublic
    elif model_name == "user":
        models = UsersPublic
    else:

        class models(SQLModel):
            data: list[model]  # type: ignore
            total: int

    @r.post(
        "/",
        response_model=model,
        tags=[model_name],
        name=model_name + "-post",
    )
    async def create_item(
        db: ASYNC_DB, item_in: model, current_user: CurrentUser
    ) -> Any:  # type: ignore
        """
        create
        """
        item_in = item_in.model_dump()
        item_in["dept_id"] = current_user.dept_id
        item_in["creator_id"] = current_user.id
        if "id" in item_in:
            del item_in["id"]
        if "create_time" in item_in:
            del item_in["create_time"]
        if "update_time" in item_in:
            del item_in["update_time"]
        item = model(**item_in)
        db.add(item)
        await db.commit()
        await db.refresh(item)
        return item

    @r.patch(
        "/{item_id}",
        response_model=model,
        tags=[model_name],
        name=model_name + "-patch",
    )
    async def update_item(db: ASYNC_DB, item_id: int, item_in: model) -> Any:  # type: ignore
        """
        update {}
        """
        if "create_time" in item_in:
            del item_in["create_time"]
        if "update_time" in item_in:
            del item_in["update_time"]
        item_db = (await db.exec(select(model).where(model.id == item_id))).first()
        if not item_db:
            raise HTTPException(status_code=404, detail=f"{model_name} not found")

        item_data = item_in.model_dump(exclude_unset=True)  # get setted fields
        extra_data = {}
        item_db.sqlmodel_update(item_data, update=extra_data)
        db.add(item_db)
        await db.commit()
        await db.refresh(item_db)
        return item_db

    @r.put(
        "/{item_id}",
        response_model=model,
        tags=[model_name],
        name=model_name + "-patch",
    )
    async def put_item(db: ASYNC_DB, item_id: int, item_in: model) -> Any:  # type: ignore
        """
        update {}
        """
        if "create_time" in item_in:
            del item_in["create_time"]
        if "update_time" in item_in:
            del item_in["update_time"]
        item_db = db.exec(select(model).where(model.id == item_id)).first()
        if not item_db:
            raise HTTPException(status_code=404, detail=f"{model_name} not found")

        item_data = item_in.model_dump(exclude_unset=True)  # get setted fields
        extra_data = {}
        item_db.sqlmodel_update(item_data, update=extra_data)
        db.add(item_db)
        await db.commit()
        await db.refresh(item_db)
        return item_db

    async def get_items(
        db: ASYNC_DB,
        permission: Permission,
        current_user: CurrentUser,
        request: Request,
        page: int = 1,
        limit: int = 10,
        values: Optional[List[str]] = Query(default=None, alias="values[]"),
    ) -> Any:
        fields = build_fields(model, values)
        extra_fields, joins = build_joins(
            model, model_alias, request.query_params, key2model
        )
        fields += extra_fields
        filters = build_filters(
            model, request.query_params, db.bind.dialect.name if db.bind else None
        )
        sorts = build_sort(model, request.query_params)

        sql = select(*fields)
        for join in joins:
            sql = sql.outerjoin(*join)
        sql = sql.where(*filters)
        sql_count = select(func.count()).where(*filters).select_from(model)

        if permission:
            if None not in permission:
                sql_count = sql_count.where(model.dept_id.in_(permission))
                sql = sql.where(model.dept_id.in_(permission))
        else:
            sql_count = sql_count.where(model.creator_id == current_user.id)
            sql = sql.where(model.creator_id == current_user.id)

        total = (await db.exec(sql_count)).one()
        items = (
            (
                await db.exec(
                    sql.offset((page - 1) * limit).order_by(*sorts).limit(limit)
                )
            )
            .mappings()
            .all()
        )
        rows = [dict(row) for row in items]
        deal_row(rows)
        return {"data": rows, "total": total}

    if cache_list is None:
        r.get(
            "/",
            tags=[model_name],
            name=model_name + "-list",
        )(get_items)
    else:
        r.get(
            "/",
            tags=[model_name],
            name=model_name + "-list",
        )(get_items)

    @r.get(
        "/{item_id}",
        response_model=model,
        tags=[model_name],
        name=model_name + "-get",
    )
    async def get_item(
        db: ASYNC_DB,
        item_id: int,
        current_user: CurrentUser,
    ) -> Any:  # type: ignore
        """
        get {}
        """
        user = (await db.exec(select(model).where(model.id == item_id))).first()
        if not user:
            raise HTTPException(status_code=404, detail=f"{model_name} not found")
        return user

    @r.delete("/{item_id}", tags=[model_name], name=model_name + "-delete")
    async def delete_item(
        db: ASYNC_DB,
        item_id: int,
        current_user: CurrentUser,
    ) -> Any:  # type: ignore
        """
        delete {}
        """
        item = (await db.exec(select(model).where(model.id == item_id))).first()
        if not item:
            raise HTTPException(status_code=404, detail=f"{model_name} not found")
        await db.delete(item)  # 可以触发删除事件

        await db.commit()
        return {"detail": f"{model_name} deleted successfully"}

    router.include_router(r, prefix=f"/{model_name}", tags=[model_name])


def init_chat(router: APIRouter | FastAPI):
    from src.chat import router as chat_router

    router.include_router(chat_router)


def initrouters(router: APIRouter | FastAPI):
    router.include_router(login.router, prefix="/login", tags=["login"])
    router.add_api_route(
        "/captcha/",
        get_captcha,
        methods=["GET"],
        response_model=bytes,
        tags=["captcha"],
        name="验证码",
    )
    router.add_api_route(
        "/image/", image, methods=["GET"], tags=["image"], name="图片流"
    )
    router.add_api_route(
        "/upload/", upload_file, methods=["POST"], tags=["upload"], name="上传文件"
    )
    router.add_api_route(
        "/uploads/",
        upload_files,
        methods=["POST"],
        tags=["uploads"],
        name="批量上传文件",
    )
    router.add_api_route(
        "/download/{file_id}/",
        download_file,
        methods=["GET"],
        tags=["download"],
        name="下载文件",
    )
    router.add_api_route(
        "/iconify_collections/",
        iconify_collections,
        methods=["GET"],
        tags=["iconify"],
        name="获取所有图标集合",
    )
    router.add_api_route(
        "/iconify_icons/",
        iconify_icons,
        methods=["GET"],
        tags=["iconify"],
        name="获取指定集合的所有图标",
    )
    router.add_api_route(
        "/me/",
        me,
        methods=["GET"],
        tags=["user"],
        name="获取当前用户信息（含权限和菜单树）",
    )
    initrouter(Interface, router)
    initrouter(Button, router)
    initrouter(Item, router)
    initrouter(Menu, router)
    initrouter(Dept, router)
    initrouter(Role, router)
    initrouter(File, router)
    initrouter(User, router)
    initrouter(LoginLog, router)
    initrouter(Model, router)  # Model 供后台管理
    init_chat(router)  # Chat WebSocket + CRUD
