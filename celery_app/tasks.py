import json
import os
import tempfile

from celery import Celery

from yt_dlp import YoutubeDL
import logging
from config_data.config import ConfigEnv, load_config
from s3.s3_client import upload_to_s3
from utils.func import sanitize_filename
from utils.trottle import del_throttle
from redis import Redis

config: ConfigEnv = load_config()

logger = logging.getLogger(__name__)
sync_redis = Redis(host=config.redis.host, port=config.redis.port, password=config.redis.password)

app = Celery(
    "tasks",
    broker=f'redis://:{config.redis.password}@{config.redis.host}:{config.redis.port}/0',
    backend=f"redis://:{config.redis.password}@{config.redis.host}:{config.redis.port}/0"
)

@app.task(name="celery_app.tasks.parse_youtube_formats")
def parse_youtube_formats(user_id, url):
    try:
        with YoutubeDL({"quiet": True}) as ydl:
            info = ydl.extract_info(url, download=False)
            formats = [
                {
                    "format_id": f["format_id"],
                    "format_note": f.get("format_note"),
                    "ext": f.get("ext"),
                    "filesize": f.get("filesize"),
                }
                for f in info["formats"]
                if f.get("ext") in ["mp4", "m4a"] and f.get("filesize")
            ]
            formats = [f for f in formats if f["filesize"] and f["filesize"] > 0]
            formats.sort(key=lambda f: f["filesize"], reverse=True)

        # Пишем в Redis
        key = f"yt_formats:{user_id}:{url}"
        sync_redis.setex(key, 600, json.dumps(formats))  # храним 10 минут

    except Exception as e:
        key = f"yt_formats:{user_id}:{url}"
        sync_redis.setex(key, 600, "error")
    finally:
        del_throttle(user_id, 'send')


@app.task(name="celery_app.tasks.download_and_upload_video")
def download_and_upload_video(url, data, user_id):
    try:
        logger.info('start celery')

        with YoutubeDL({"quiet": True}) as ydl:
            info = ydl.extract_info(url, download=False)

        _, format_id = data.split("|")
        title = sanitize_filename(info["title"])
        format_info = next(
            f for f in info["formats"]
            if f["format_id"] == format_id and f.get("ext")
        )
        quality = format_info.get("format_note") or format_id
        ext = format_info.get("ext", "mp4")

        tmp_dir = tempfile.gettempdir()
        filename_base = f"{title}_{quality}.{ext}"

        # with tempfile.NamedTemporaryFile(delete=False) as tmp:
        #     tmp_path = tmp.name

        full_path = os.path.join(tmp_dir, filename_base)

        ydl_opts = {
            "format": format_id,
            "outtmpl": full_path,
            "quiet": True,
        }

        with YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        with open(full_path, "rb") as f:
            s3_key = f"user_videos/{user_id}/{filename_base}"
            s3_url = upload_to_s3(f, s3_key)

        # Кладем ссылку в Redis
        redis_key = f"s3||result||{user_id}||{url}"
        sync_redis.set(redis_key, s3_url, ex=3600)
        logger.info(f'Отправлен кей: {redis_key}')
        try:

            os.remove(full_path)
        except Exception:
            pass

    except Exception as e:
        logger.exception(f"Ошибка в Celery-задаче: {e}")
        sync_redis.set(f"s3||result||{user_id}||{url}", "error", ex=600)

    finally:
        del_throttle(user_id, 'dl')
