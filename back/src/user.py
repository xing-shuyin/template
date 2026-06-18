from pydantic import EmailStr
from fastapi import APIRouter
from sqlmodel import select
from src.deps import DB, CurrentUser, ASYNC_DB
from security import hash_password, verify_password
from models import User, UserCreate, UserPublic, UserUpdate, Role, Button, Interface, Menu

router = APIRouter()


async def get_user(db: ASYNC_DB, email: EmailStr) -> User | None:
    return (await db.exec(select(User).where(User.email == email))).first()


async def authenticate(*, db: ASYNC_DB, email: EmailStr, password: str) -> User | None:
    user = await get_user(db, email)
    if user:
        if verify_password(password, user.hash_password):
            return user
    else:
        # 对不存在的用户也执行虚拟哈希比较，防止时序攻击
        verify_password(password, "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW")
    return None


def create_user(*, db: DB, user_in: UserCreate) -> User:
    user = User.model_validate(
        user_in, update={"hash_password": hash_password(user_in.password)}
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def update_user(*, db: DB, user_db: User, user_in: UserUpdate) -> User:
    user_data = user_in.model_dump(exclude_unset=True)  # get setted fields
    extra_data = {}
    if user_in.password:
        extra_data["hash_password"] = hash_password(user_in.password)
    user_db.sqlmodel_update(user_data, update=extra_data)
    db.add(user_db)
    db.commit()
    db.refresh(user_db)
    return user_db


async def me(db: ASYNC_DB, current_user: CurrentUser):
    """返回当前用户信息、权限、过滤后的菜单树"""
    user_info = {"id": current_user.id, "email": current_user.email, "fullname": current_user.fullname,
                 "avatar": current_user.avatar, "is_superuser": current_user.is_superuser,
                 "roles": current_user.roles or []}
    permissions = {"buttons": [], "interfaces": [], "menus": []}
    if current_user.roles:
        roles = (await db.exec(select(Role).where(Role.id.in_(current_user.roles)))).all()
        btn_ids, iface_ids, menu_ids = set(), set(), set()
        for r in roles:
            btn_ids.update(r.buttons or [])
            iface_ids.update(r.interfaces or [])
            menu_ids.update(r.menus or [])
        if btn_ids:
            buttons = (await db.exec(select(Button).where(Button.id.in_(btn_ids)))).all()
            permissions["buttons"] = [b.code for b in buttons]
        if iface_ids:
            permissions["interfaces"] = list(iface_ids)
        if menu_ids:
            permissions["menus"] = list(menu_ids)

    # 构建菜单树
    all_menus = (await db.exec(select(Menu).order_by(Menu.sort))).all()
    menu_list = []
    for m in all_menus:
        menu_list.append({"id": m.id, "parent_id": m.parent_id, "label": m.label,
                          "icon": m.icon, "name": m.name, "path": m.path,
                          "component": m.component, "is_catalog": m.is_catalog,
                          "sort": m.sort, "is_link": m.is_link})

    allowed_menu_ids = set(permissions["menus"])
    if current_user.is_superuser:
        visible_menus = menu_list
    elif allowed_menu_ids:
        visible_ids = set(allowed_menu_ids)
        for m in menu_list:
            if m["id"] in allowed_menu_ids and m["parent_id"]:
                visible_ids.add(m["parent_id"])
        visible_menus = [m for m in menu_list if m["id"] in visible_ids]
    else:
        visible_menus = []

    def build_tree(items, parent=None):
        tree = []
        for item in items:
            if item["parent_id"] == parent:
                children = build_tree(items, item["id"])
                node = {k: v for k, v in item.items() if k != "parent_id"}
                if children:
                    node["children"] = children
                tree.append(node)
        return tree

    # 去掉 is_catalog 在构建树时无用字段
    return {
        "user": user_info,
        "permissions": permissions,
        "menus_tree": build_tree(visible_menus),
    }
