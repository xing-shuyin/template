"""
AI 对话 WebSocket 处理器

协议:
  Client → Server: {"action": "send",   "messages": [...], "model_id": 1, "chat_id": 123}
  Client → Server: {"action": "stop"}
  Server → Client: {"type": "delta",    "content": "..."}            — 增量内容
  Server → Client: {"type": "reason",   "content": "..."}            — 思考过程
  Server → Client: {"type": "tool_calls", "data": [...]}             — 工具调用
  Server → Client: {"type": "end"}                                    — 结束
  Server → Client: {"type": "error",    "message": "..."}            — 错误
"""

from sqlmodel import select, delete
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, HTTPException
from src.deps import ASYNC_DB, CurrentUserId, current_user_id
from models import Chat, Model
import json
import asyncio
import uuid
from loguru import logger

router = APIRouter(prefix="/chat", tags=["chat"])

# 存储运行中的生成任务, key=uuid, value=asyncio.Event 用于停止信号
_tasks: dict[str, asyncio.Event] = {}


# ─── AI 流式调用 ─────────────────────────────────────────────

async def stream_ai(
    messages: list[dict],
    model_config: Model | None,
):
    """调用 AI API 并逐块 yield 响应数据。"""
    if model_config is None:
        # 模拟响应 (无可用模型时演示用)
        yield {"type": "reason", "content": "思考中..."}
        await asyncio.sleep(0.5)
        yield {"type": "delta", "content": "你好！我是 AI 助手。"}
        await asyncio.sleep(0.2)
        yield {"type": "delta", "content": "当前没有配置 AI 模型，这是模拟回复。"}
        await asyncio.sleep(0.2)
        yield {"type": "delta", "content": "\n\n请先在后台添加一个 Model 记录来启用真实 AI。"}
        return

    # ── 真实 OpenAI 兼容 API 调用 ──
    import httpx
    base_url = (model_config.base_url or "https://api.openai.com/v1").rstrip("/")
    api_key = model_config.api_key or "sk-placeholder"

    async with httpx.AsyncClient(timeout=120) as client:
        try:
            async with client.stream(
                "POST",
                f"{base_url}/chat/completions",
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": model_config.name,
                    "messages": messages,
                    "stream": True,
                },
            ) as resp:
                resp.raise_for_status()
                buffer = ""
                async for chunk in resp.aiter_bytes():
                    buffer += chunk.decode()
                    while "\n" in buffer:
                        line, buffer = buffer.split("\n", 1)
                        line = line.strip()
                        if not line or line.startswith(":"):
                            continue
                        if line.startswith("data: "):
                            data_str = line[6:]
                            if data_str == "[DONE]":
                                return
                            try:
                                data = json.loads(data_str)
                            except json.JSONDecodeError:
                                continue
                            for choice in data.get("choices", []):
                                delta = choice.get("delta", {})
                                finish = choice.get("finish_reason")
                                if delta.get("content"):
                                    yield {"type": "delta", "content": delta["content"]}
                                if delta.get("reasoning_content"):
                                    yield {"type": "reason", "content": delta["reasoning_content"]}
                                if delta.get("tool_calls"):
                                    yield {"type": "tool_calls", "data": delta["tool_calls"]}
                                if finish == "tool_calls":
                                    yield {"type": "tool_calls_end"}
        except httpx.HTTPStatusError as e:
            body = await e.response.aread()
            yield {"type": "error", "message": f"API {e.response.status_code}: {body.decode(errors='replace')[:500]}"}
        except Exception as e:
            yield {"type": "error", "message": str(e)}


# ─── WebSocket 端点 ──────────────────────────────────────────

@router.websocket("/ws")
async def chat_ws(websocket: WebSocket, db: ASYNC_DB):
    await websocket.accept()
    user_id = await current_user_id(db=db, token_bearer="", token_cookie="")
    # 尝试从 query 参数拿 token
    token = websocket.query_params.get("token") or websocket.query_params.get("access_token")
    if token:
        from src.deps import parse_token, TokenType
        payload = parse_token(token, TokenType.access_token, raise_error=False)
        if payload:
            from sqlmodel import select
            from models import User
            user_obj = (await db.exec(select(User).where(User.id == int(payload.sub)))).first()
            if user_obj:
                user_id = user_obj.id

    task_id = str(uuid.uuid4())
    stop_event = asyncio.Event()
    _tasks[task_id] = stop_event

    logger.info(f"[WS] 新连接 {task_id}, user_id={user_id}")

    try:
        while True:
            raw = await websocket.receive_json()
            action = raw.get("action")

            if action == "send":
                stop_event.clear()
                raw_messages = raw.get("messages", [])
                model_id = raw.get("model_id")

                # Build messages for AI: process uploads temporarily, don't modify originals
                import os
                from settings import settings
                ai_messages = []
                for m in raw_messages:
                    content = m.get("content", "")
                    if m.get("role") == "user" and m.get("uploads"):
                        parts = [content] if content else []
                        for upl in m["uploads"]:
                            fpath = os.path.join(settings.MEDIA_PATH, upl.get("url", ""))
                            if os.path.exists(fpath):
                                try:
                                    with open(fpath, "r", encoding="utf-8", errors="replace") as fh:
                                        txt = fh.read()
                                    parts.append(f"--- {upl.get('name', 'file')} ---\n{txt}")
                                except Exception:
                                    pass
                        ai_content = "\n\n".join(parts)
                    else:
                        ai_content = content
                    ai_messages.append({"role": m["role"], "content": ai_content})

                model_obj = None
                if model_id:
                    result = await db.exec(select(Model).where(Model.id == int(model_id)))
                    model_obj = result.first()

                chat_id = raw.get("chat_id")

                async def _generate():
                    try:
                        last_user_msg = next((m for m in reversed(ai_messages) if m.get("role") == "user"), None)
                        content_preview = ""
                        if last_user_msg:
                            c = last_user_msg.get("content", "")
                            content_preview = c[:15] if isinstance(c, str) else str(c)[:15]

                        assistant_content = ""
                        async for chunk in stream_ai(ai_messages, model_obj):
                            if stop_event.is_set():
                                await websocket.send_json({"type": "cancelled"})
                                return
                            await websocket.send_json(chunk)
                            if chunk.get("type") == "delta":
                                assistant_content += chunk.get("content", "")

                        await websocket.send_json({"type": "end"})

                        # 保存消息到数据库
                        if chat_id:
                            result = await db.exec(select(Chat).where(Chat.id == int(chat_id)))
                            chat_obj = result.first()
                            if chat_obj:
                                store_messages = raw_messages + [{"role": "assistant", "content": assistant_content}]
                                chat_obj.messages = store_messages
                                db.add(chat_obj)
                                await db.commit()
                    except Exception as e:
                        logger.error(f"[WS] 生成错误: {e}")
                        try:
                            await websocket.send_json({"type": "error", "message": str(e)})
                        except Exception:
                            pass

                asyncio.create_task(_generate())

            elif action == "stop":
                stop_event.set()

    except WebSocketDisconnect:
        logger.info(f"[WS] 断开 {task_id}")
    except Exception as e:
        logger.error(f"[WS] 异常: {e}")
    finally:
        _tasks.pop(task_id, None)


# ─── REST CRUD (复用 initrouter 风格) ───────────────────────

@router.get("/", tags=["chat"])
async def list_chats(
    db: ASYNC_DB,
    current_user_id: CurrentUserId,
    page: int = 1,
    limit: int = 100,
    model: str = "",
    sort: str = "-created_at",
):
    from sqlmodel import func, desc
    filters = [Chat.creator_id == current_user_id] if current_user_id else []
    if model:
        filters.append(Chat.model == model)
    order = desc(Chat.created_at) if sort.startswith("-") else Chat.created_at
    total = (await db.exec(select(func.count()).where(*filters).select_from(Chat))).one()
    items = (
        await db.exec(
            select(Chat).where(*filters).order_by(order).offset((page - 1) * limit).limit(limit)
        )
    ).all()
    # 只返回必要字段
    result = []
    for c in items:
        result.append({
            "id": c.id,
            "name": c.name,
            "model": c.model,
            "role_id": c.role_id,
            "created_at": str(c.created_at) if c.created_at else None,
        })
    return {"data": result, "total": total}


@router.post("/", tags=["chat"])
async def create_chat(db: ASYNC_DB, chat_in: Chat, current_user_id: CurrentUserId):
    data = chat_in.model_dump()
    data.pop("id", None)
    data.pop("created_at", None)
    data.pop("updated_at", None)
    data["creator_id"] = current_user_id
    chat = Chat(**data)
    db.add(chat)
    await db.commit()
    await db.refresh(chat)
    return chat


@router.get("/{chat_id}", tags=["chat"])
async def get_chat(db: ASYNC_DB, chat_id: int):
    result = (await db.exec(select(Chat).where(Chat.id == chat_id))).first()
    if not result:
        raise HTTPException(404, "Chat not found")
    return result


@router.patch("/{chat_id}", tags=["chat"])
async def update_chat(db: ASYNC_DB, chat_id: int, chat_in: Chat):
    db_obj = (await db.exec(select(Chat).where(Chat.id == chat_id))).first()
    if not db_obj:
        raise HTTPException(404, "Chat not found")
    data = chat_in.model_dump(exclude_unset=True)
    data.pop("created_at", None)
    data.pop("updated_at", None)
    data.pop("id", None)
    for k, v in data.items():
        setattr(db_obj, k, v)
    db.add(db_obj)
    await db.commit()
    await db.refresh(db_obj)
    return db_obj


@router.delete("/{chat_id}", tags=["chat"])
async def delete_chat(db: ASYNC_DB, chat_id: int):
    db_obj = (await db.exec(select(Chat).where(Chat.id == chat_id))).first()
    if not db_obj:
        raise HTTPException(404, "Chat not found")
    await db.exec(delete(Chat).where(Chat.id == chat_id))
    await db.commit()
    return {"detail": "deleted"}


# ─── 模型查询 ────────────────────────────────────────────────

@router.get("/models/", tags=["chat"])
async def list_models(db: ASYNC_DB):
    items = (await db.exec(select(Model))).all()
    return {"data": items}
