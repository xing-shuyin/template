import datetime
from email.message import EmailMessage
import json
import random
import smtplib
import string
from typing import Optional, Annotated
import uuid
import httpx
from settings import settings
from jinja2 import Environment, FileSystemLoader
from sqlmodel import SQLModel, select
from fastapi import Cookie, Depends, HTTPException, Header, UploadFile, Body
from fastapi.responses import FileResponse, JSONResponse, StreamingResponse
import io
from PIL import Image, ImageDraw, ImageFont
import requests
import hashlib
import os
from io import BytesIO
from pathlib import Path
from src.deps import DB, Client, ASYNC_DB
from cache import get_cache
from models import File
from src.deps import CurrentUser
from loguru import logger
import base64


async def upload_file(db: ASYNC_DB, file: UploadFile, user: CurrentUser) -> dict:
    now = datetime.datetime.now()
    year = str(now.year)
    month = str(now.month)
    day = str(now.day)
    url = "upload" + "/" + year + "/" + month + "/" + day + "/"
    if not os.path.exists(os.path.join(settings.MEDIA_PATH, url)):
        os.makedirs(os.path.join(settings.MEDIA_PATH, url))

    url += str(uuid.uuid4()) + "." + file.filename
    file_path = Path(os.path.join(settings.MEDIA_PATH, url))

    with open(file_path, "wb") as buffer:
        buffer.write(file.file.read())
    f = File(name=file.filename, url=url, size=file.file.tell(), type=file.content_type)
    db.add(f)
    await db.commit()
    return {
        "name": file.filename,
        "url": url,
        "id": f.id,
        "size": file.file.tell(),
        "type": file.content_type,
    }


async def upload_files(
    db: ASYNC_DB,
    files: list[UploadFile],
    user: CurrentUser,
):
    now = datetime.datetime.now()
    year = str(now.year)
    month = str(now.month)
    day = str(now.day)
    url = "upload" + "/" + year + "/" + month + "/" + day + "/"
    if not os.path.exists(os.path.join(settings.MEDIA_PATH, url)):
        os.makedirs(os.path.join(settings.MEDIA_PATH, url))

    file_list = []
    for file in files:
        file_url = url + str(uuid.uuid4()) + "." + file.filename
        file_path = Path(os.path.join(settings.MEDIA_PATH, file_url))
        with open(file_path, "wb") as buffer:
            buffer.write(file.file.read())
        f = File(
            name=file.filename,
            url=file_url,
            size=file.file.tell(),
            type=file.content_type,
        )
        db.add(f)
        await db.commit()
        file_list.append(
            {
                "name": file.filename,
                "url": file_url,
                "id": f.id,
                "size": file.file.tell(),
                "type": file.content_type,
            }
        )

    return file_list


async def download_file(db: ASYNC_DB, file_id: int) -> FileResponse:
    file = (await db.exec(select(File).where(File.id == file_id))).first()
    if not file:
        raise HTTPException(status_code=404, detail="file not found")
    file_path = os.path.join(settings.MEDIA_PATH, file.url)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="file not found")
    return FileResponse(Path(file_path), filename=file.name)


env = Environment(
    loader=FileSystemLoader(os.path.join(settings.MEDIA_PATH, "templates"))
)


def send_email(to_email: str, content: str, subject: str = "") -> bool:
    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = settings.EMAILS_FROM_EMAIL
    msg["To"] = to_email
    msg.add_alternative(content, subtype="html")

    if settings.SMTP_SSL:
        with smtplib.SMTP_SSL(settings.SMTP_HOST, settings.SMTP_PORT) as server:
            server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
            server.sendmail(settings.EMAILS_FROM_EMAIL, to_email, msg.as_string())
            return True
    else:
        with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
            server.starttls()
            server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
            server.sendmail(settings.EMAILS_FROM_EMAIL, to_email, msg.as_string())
            return True


def send_activate_email(
    to_email: str, user_name: str, activate_link: str, expiration_time: str
) -> bool:
    template = env.get_template("activate_email.html")
    content = template.render(
        user_name=user_name,
        activate_link=activate_link,
        expiration_time=expiration_time,
    )
    return send_email(to_email, content, "账号激活")


def send_code_email(
    to_email: str, user_name: str, verification_code: str, expiration_time: str
) -> None:
    template = env.get_template("code_email.html")
    content = template.render(
        user_name=user_name,
        verification_code=verification_code,
        expiration_time=expiration_time,
    )
    send_email(to_email, content, "验证码")


def send_reset_email(
    to_email: str, user_name: str, reset_link: str, expiration_time: str
) -> bool:
    template = env.get_template("reset_email.html")
    content = template.render(
        user_name=user_name, reset_link=reset_link, expiration_time=expiration_time
    )
    send_email(to_email, content, "重置密码")


class CaptchaConfig(SQLModel):
    width: int = 100
    height: int = 40
    font_size: int = 20
    char_length: int = 4


def generate_captcha_text(length: int = 4) -> str:
    return "".join(random.choices(string.ascii_uppercase + string.digits, k=length))


def generate_captcha_image(text: str, config: CaptchaConfig) -> Image.Image:
    image = Image.new("RGB", (config.width, config.height), (255, 255, 255))
    draw = ImageDraw.Draw(image)

    try:
        font = ImageFont.truetype("arial.ttf", config.font_size)
    except IOError:
        font = ImageFont.load_default()

    for i, char in enumerate(text):
        position = (10 + i * (config.width // config.char_length), 10)
        draw.text(position, char, font=font, fill=(0, 0, 0))

    for _ in range(5):
        start = (random.randint(0, config.width), random.randint(0, config.height))
        end = (random.randint(0, config.width), random.randint(0, config.height))
        draw.line([start, end], fill=(0, 0, 0), width=1)

    return image


async def get_captcha(
    client: Client,
    config: CaptchaConfig = Depends(),
    session_id: Optional[str] = Cookie(None),
) -> dict:
    if not session_id:
        session_id = str(uuid.uuid4())
    text = generate_captcha_text(config.char_length)
    image = generate_captcha_image(text, config)

    buffer = io.BytesIO()
    image.save(buffer, format="PNG")
    buffer.seek(0)
    await get_cache().set(session_id, text, ex=300)

    image_base64 = base64.b64encode(buffer.getvalue()).decode("utf-8")

    response_data = {"session_id_form": session_id, "image": image_base64}
    response = JSONResponse(content=response_data)

    response.set_cookie(
        "session_id_cookie",
        session_id,
        httponly=False,
        secure=False,
        expires=datetime.datetime.now(datetime.timezone.utc)
        + datetime.timedelta(days=50),
    )

    return response


async def image(file: str) -> FileResponse:
    if "http" not in file:
        img_path = os.path.join(settings.MEDIA_PATH, file)
        return FileResponse(img_path)
    try:
        n = hashlib.md5(file.encode("utf-8")).hexdigest()
        p = os.path.join(settings.MEDIA_PATH, "image", f"{n}.jpg")
        if not os.path.exists(p):
            res = requests.get(file)
            if res.status_code == 200:
                img = Image.open(BytesIO(res.content))
                img.save(p)
            else:
                raise HTTPException(status_code=500, detail="缓存失败")
        return FileResponse(p)
    except:
        raise HTTPException(status_code=500, detail="缓存失败")


async def video(file: str, range: str = Header(None)) -> StreamingResponse:
    try:
        video_path = Path(os.path.join(settings.MEDIA_PATH, file))
        if not video_path.exists():
            raise HTTPException(status_code=404, detail="视频不存在")

        filesize = video_path.stat().st_size

        if not range:
            CHUNK_SIZE = min(1024 * 1024, filesize)
            range = f"bytes=0-{CHUNK_SIZE - 1}"

        start, end = range.replace("bytes=", "").split("-")
        start = int(start)
        end = int(end) if end else min(start + 1024 * 1024, filesize - 1)
        end = min(end, filesize - 1)

        content_length = end - start + 1
        headers = {
            "Content-Range": f"bytes {start}-{end}/{filesize}",
            "Accept-Ranges": "bytes",
            "Content-Length": str(content_length),
        }

        def iterfile():
            with open(video_path, "rb") as f:
                f.seek(start)
                remaining = content_length
                while remaining > 0:
                    chunk_size = min(4096, remaining)
                    chunk = f.read(chunk_size)
                    if not chunk:
                        break
                    remaining -= len(chunk)
                    yield chunk

        return StreamingResponse(
            iterfile(), status_code=206, headers=headers, media_type="video/mp4"
        )
    except Exception as e:
        logger.error(f"Error in video endpoint: {e}")


async def iconify_collections() -> JSONResponse:
    os.makedirs(os.path.join(settings.MEDIA_PATH, "iconify"), exist_ok=True)
    cache_file = os.path.join(
        settings.MEDIA_PATH, "iconify", "iconify_collections.json"
    )
    if os.path.exists(cache_file):
        with open(cache_file, "r", encoding="utf-8") as f:
            if (
                datetime.datetime.now()
                - datetime.datetime.fromtimestamp(os.path.getctime(cache_file))
            ).total_seconds() < 3000000:
                return JSONResponse(
                    json.load(f), media_type="application/json", status_code=200
                )
    # 使用异步 HTTP 客户端，避免阻塞事件循环
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            r = await client.get("https://api.iconify.design/collections")
            data = r.json()
        with open(cache_file, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        return JSONResponse(data, media_type="application/json", status_code=200)
    except httpx.TimeoutException:
        logger.error("请求 Iconify API 超时")
        return JSONResponse({"error": "请求超时，请稍后重试"}, status_code=504)
    except Exception as e:
        logger.error(f"请求 Iconify API 失败: {e}")
        return JSONResponse({"error": str(e)}, status_code=500)


async def iconify_icons(prefix: str) -> JSONResponse:
    cache_file = os.path.join(
        settings.MEDIA_PATH, "iconify", f"iconify_icons_{prefix}.json"
    )
    if os.path.exists(cache_file):
        with open(cache_file, "r", encoding="utf-8") as f:
            if (
                datetime.datetime.now()
                - datetime.datetime.fromtimestamp(os.path.getctime(cache_file))
            ).total_seconds() < 3000000:
                return JSONResponse(
                    json.load(f), media_type="application/json", status_code=200
                )
    # 使用异步 HTTP 客户端，避免阻塞事件循环
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            r = await client.get(
                "https://api.iconify.design/collection",
                params={"prefix": prefix, "pretty": 1},
            )
            data = r.json()
        with open(cache_file, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        return JSONResponse(data, media_type="application/json", status_code=200)
    except httpx.TimeoutException:
        logger.error(f"请求 Iconify API 超时 (prefix: {prefix})")
        return JSONResponse({"error": "请求超时，请稍后重试"}, status_code=504)
    except Exception as e:
        logger.error(f"请求 Iconify API 失败: {e}")
        return JSONResponse({"error": str(e)}, status_code=500)
