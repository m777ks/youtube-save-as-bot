import json

from aiogram import Bot
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from db.ORM import DataBase
from redis_client.client_redis import redis_client
from utils.check_limit import incr_download
ERROR_MSG = ("❌ Произошла ошибка при загрузке видео.\n\n"
             "Пожалуйста, отправьте <b>прямую ссылку на видео</b>, например:\n"
             "https://youtu.be/VIDEO_ID\nили\nhttps://www.youtube.com/watch?v=VIDEO_ID\n\n"
             "⚠️ Ссылки на плейлисты, каналы или сборники не поддерживаются.")

async def check_s3_results(bot: Bot):
    keys = await redis_client.keys("s3||result||*")
    for key in keys:
        user_id = int(key.decode().split("||")[-2])

        try:
            print(f"Получен кей: {key}")
            print(f'USER_ID: {user_id}')
            url_orig = key.decode().split("||")[-1]
            url = await redis_client.get(key)
            url = url.decode() if url else None

            if url == "error":
                await bot.send_message(user_id, ERROR_MSG)
            elif url:
                button = InlineKeyboardButton(text="🔗 Скачать видео", url=url)
                markup = InlineKeyboardMarkup(inline_keyboard=[[button]])
                await bot.send_message(user_id, f"✅ Готово! <a href='{url_orig}'>Твое видео готово к скачиванию.</a>\nНажми на кнопку ниже:",
                    reply_markup=markup, parse_mode='HTML')
                await incr_download(user_id, url_orig)
                await DataBase.log_download(user_id, url_orig)

            await redis_client.delete(key)  # удаляем ключ, чтобы не повторялось

        except Exception as e:
            await redis_client.delete(key)
            print(f'ERROR: send user: {key}, error: {e}')

            await bot.send_message(user_id, ERROR_MSG)


async def check_formats_ready(bot: Bot):
    # Найти все ключи yt_formats:* (или по user_id)
    keys = await redis_client.keys("yt_formats:*")
    for key in keys:
        key_str = key.decode() if isinstance(key, bytes) else key
        parts = key_str.split(":")
        user_id = int(parts[1])
        try:

            url = ":".join(parts[2:])
            value = await redis_client.get(key)
            value = value.decode() if value else None

            if not value:
                continue
            if value == "error":
                await bot.send_message(user_id, "❌ Не удалось получить форматы видео.")
                await redis_client.delete(key)
                continue

            formats = json.loads(value)
            if not formats:
                await bot.send_message(user_id, "❌ Не удалось найти подходящие форматы.")
                await redis_client.delete(key)
                continue

            buttons = []
            for f in formats[:10]:
                fid = f["format_id"]
                filesize_mb = round(f["filesize"] / 1024 / 1024, 1)
                label = f"{f.get('format_note') or ''} {f['ext']} - {filesize_mb}MB"
                redis_key = f"yt:{user_id}:{fid}"
                await redis_client.setex(redis_key, 3600, url)
                buttons.append([InlineKeyboardButton(text=label.strip(), callback_data=f"dl|{fid}")])
            keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
            await bot.send_message(user_id, "Выбери качество:", reply_markup=keyboard)

            await redis_client.delete(key)
        except Exception as e:
            print(f"Ошибка при отправке форматов: {e}")
            await redis_client.delete(key)
            await bot.send_message(user_id, ERROR_MSG)