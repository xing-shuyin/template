"""
AI 对话处理器 — 基于 LangChain

协议 (WebSocket):
  Client → Server: {"action": "send", "messages": [...], "model_id": 1, "chat_id": 123}
  Client → Server: {"action": "stop"}
  Server → Client: {"type": "delta", "content": "..."}
  Server → Client: {"type": "reason", "content": "..."}
  Server → Client: {"type": "tool_calls", "data": [...]}
  Server → Client: {"type": "end"}
  Server → Client: {"type": "error", "message": "..."}

协议 (SSE /proxy):
  OpenAI 兼容 SSE 流，供 @ai-sdk/vue useChat 使用。
"""

from sqlmodel import select, delete
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, HTTPException, Request
from fastapi.responses import StreamingResponse
from src.deps import ASYNC_DB, CurrentUserId, CurrentUser, current_user_id
from models import Chat, Model
import json
import asyncio
import uuid
from datetime import datetime
from loguru import logger

router = APIRouter(prefix="/chat", tags=["chat"])

# 存储运行中的生成任务, key=uuid, value=asyncio.Event 用于停止信号
_tasks: dict[str, asyncio.Event] = {}

# 支持的工具定义（后续可扩展）
AVAILABLE_TOOLS = []


# ─── LangChain 模型工厂 ─────────────────────────────────────

def _build_llm(model_config: Model):
    """根据 Model 数据库记录构建 LangChain LLM 实例。"""
    provider = (model_config.type or "openai").lower()
    kwargs = {
        "model": model_config.name,
        "temperature": 0.7,
        "streaming": True,
        "timeout": 120,
    }

    if provider == "anthropic":
        from langchain_anthropic import ChatAnthropic
        if model_config.api_key:
            kwargs["anthropic_api_key"] = model_config.api_key
        if model_config.base_url:
            kwargs["anthropic_api_url"] = model_config.base_url
        return ChatAnthropic(**kwargs)
    else:
        # 默认: OpenAI 兼容 (也支持 DeepSeek / Ollama / vLLM 等)
        from langchain_openai import ChatOpenAI
        if model_config.api_key:
            kwargs["openai_api_key"] = model_config.api_key
        if model_config.base_url:
            kwargs["openai_api_base"] = model_config.base_url.rstrip("/")
        return ChatOpenAI(**kwargs)


# ─── AI 流式调用 (LangChain) ────────────────────────────────

async def stream_ai(
    messages: list[dict],
    model_config: Model | None,
    enable_tools: bool = False,
):
    """使用 LangChain 调用 AI 并逐块 yield 响应数据。"""
    if model_config is None:
        yield {"type": "reason", "content": "思考中..."}
        await asyncio.sleep(0.5)
        yield {"type": "delta", "content": "你好！我是 AI 助手。"}
        await asyncio.sleep(0.2)
        yield {"type": "delta", "content": "当前没有配置 AI 模型，这是模拟回复。"}
        await asyncio.sleep(0.2)
        yield {"type": "delta", "content": "\n\n请先在后台添加一个 Model 记录来启用真实 AI。"}
        return

    llm = _build_llm(model_config)

    # 绑定工具
    if enable_tools and AVAILABLE_TOOLS:
        llm = llm.bind_tools(AVAILABLE_TOOLS)

    try:
        async for chunk in llm.astream(messages):
            # ⬇ 处理 reasoning_content (OpenAI o1/o3 专属)
            if hasattr(chunk, "additional_kwargs"):
                reason = chunk.additional_kwargs.get("reasoning_content")
                if reason:
                    yield {"type": "reason", "content": reason}

            # ⬇ 处理普通文本增量
            if chunk.content:
                yield {"type": "delta", "content": chunk.content}

            # ⬇ 处理工具调用
            if chunk.tool_call_chunks:
                for tc in chunk.tool_call_chunks:
                    yield {"type": "tool_calls", "data": tc}
                yield {"type": "tool_calls_end"}

    except Exception as e:
        logger.error(f"[LangChain] 调用失败: {e}")
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


# ─── SSE 代理端点 (供 @ai-sdk/vue useChat 调用) ─────────────

@router.post("/proxy")
async def chat_proxy(
    request: Request,
    db: ASYNC_DB,
    current_user: CurrentUser,
):
    """
    OpenAI 兼容的 SSE 流式代理端点。
    与 @ai-sdk/vue useChat 直接对接，自动保存对话到数据库。
    """
    body = await request.json()
    messages = body.get("messages", [])
    model_id = body.get("model_id")
    chat_id = body.get("chat_id")
    system_prompt = body.get("system_prompt", "")

    # 查找模型配置
    model_obj = None
    if model_id:
        result = await db.exec(select(Model).where(Model.id == int(model_id)))
        model_obj = result.first()

    # 构建 AI 消息（前置 system prompt）
    ai_messages = []
    if system_prompt:
        ai_messages.append({"role": "system", "content": system_prompt})
    for m in messages:
        if m.get("role") == "system":
            continue  # 已前置
        ai_messages.append({"role": m["role"], "content": m.get("content", "")})

    if not chat_id:
        raise HTTPException(status_code=400, detail="缺少 chat_id，请先创建对话")

    async def event_generator():
        full_content = ""
        try:
            async for chunk in stream_ai(ai_messages, model_obj):
                if chunk["type"] == "delta":
                    content = chunk["content"]
                    full_content += content
                    data = {
                        "choices": [{"delta": {"content": content}, "index": 0}]
                    }
                    yield f"data: {json.dumps(data, ensure_ascii=False)}\n\n"
                elif chunk["type"] == "reason":
                    data = {
                        "choices": [{
                            "delta": {"reasoning_content": chunk["content"]},
                            "index": 0,
                        }]
                    }
                    yield f"data: {json.dumps(data, ensure_ascii=False)}\n\n"
                elif chunk["type"] == "error":
                    data = {"error": {"message": chunk["message"]}}
                    yield f"data: {json.dumps(data, ensure_ascii=False)}\n\n"
                    return

            yield "data: [DONE]\n\n"

            # ── 保存对话到数据库 ──
            if not full_content:
                return

            user_msgs = [m for m in messages if m.get("role") == "user"]
            first_content = user_msgs[0].get("content", "") if user_msgs else ""
            store_name = first_content[:50] if first_content else "新对话"
            store_messages = messages + [{"role": "assistant", "content": full_content}]

            result = await db.exec(select(Chat).where(Chat.id == int(chat_id)))
            chat_obj = result.first()
            if chat_obj:
                chat_obj.messages = store_messages
                chat_obj.last_message_at = datetime.now()
                if not chat_obj.name:
                    chat_obj.name = store_name
                chat_obj.model = model_obj.name if model_obj else chat_obj.model
                db.add(chat_obj)
                await db.commit()

        except Exception as e:
            logger.error(f"[SSE] 代理错误: {e}")
            data = {"error": {"message": str(e)}}
            yield f"data: {json.dumps(data, ensure_ascii=False)}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
            "Connection": "keep-alive",
        },
    )


# ─── REST CRUD (复用 initrouter 风格) ───────────────────────

@router.get("/", tags=["chat"])
async def list_chats(
    db: ASYNC_DB,
    current_user: CurrentUser,
    page: int = 1,
    limit: int = 100,
    sort: str = "-created_at",
    name__contains: str = "",
    model__contains: str = "",
):
    from sqlmodel import func, desc
    filters = []
    # 非超级用户只看自己的对话
    if not current_user.is_superuser:
        filters.append(Chat.creator_id == current_user.id)
    if name__contains:
        filters.append(Chat.name.like(f"%{name__contains}%"))
    if model__contains:
        filters.append(Chat.model.like(f"%{model__contains}%"))
    if sort.startswith("-"):
        order = desc(getattr(Chat, sort[1:], Chat.created_at))
    else:
        order = getattr(Chat, sort, Chat.created_at)
    total = (await db.exec(select(func.count()).where(*filters).select_from(Chat))).one()
    items = (
        await db.exec(
            select(Chat).where(*filters).order_by(order).offset((page - 1) * limit).limit(limit)
        )
    ).all()
    return {"data": items, "total": total}


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
