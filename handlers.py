import asyncio
import glob
import logging
import os
import re
import tempfile
import time

from aiogram import Router, types, F, Bot
from aiogram.filters import CommandStart, Command
from aiogram.types import FSInputFile, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from pytube import YouTube
from yt_dlp import YoutubeDL
from celery_app.tasks import download_and_upload_video, parse_youtube_formats
from redis_client.client_redis import redis_client
from s3.s3_client import upload_to_s3
from utils.check_limit import can_download
from utils.trottle import del_throttle, check_throttle
from db.ORM import DataBase

router = Router()

logging.basicConfig(level=logging.INFO)

DOWNLOAD_DIR = "downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)


@router.message(CommandStart())
async def start_cmd(message: types.Message):
    if await check_throttle(message.from_user.id, message.text):
        return
    await message.reply("Привет! Пришли мне ссылку на видео с YouTube, и я скачаю его для тебя.")

    user_name = message.from_user.username or "NO_USERNAME"
    user = await DataBase.insert_user(message.from_user.id, user_name)

SUPPORT_TEXT = (
    "✉️ <b>Связаться с поддержкой</b>\n\n"
    "Если у вас возникли вопросы, предложения или что-то не работает — "
    "просто напишите админу: <a href='https://t.me/Raymond_send'>@Raymond_send</a>.\n\n"
    "Постараемся помочь максимально быстро!\n"
    "Спасибо, что пользуетесь ботом 🙌"
)

@router.message(Command(commands="supports"))
async def supports_handler(message: types.Message):
    if await check_throttle(message.from_user.id, message.text):
        return
    await message.answer(SUPPORT_TEXT, parse_mode="HTML")

@router.message(lambda m: "youtu" in m.text)
async def on_youtube_link(message: types.Message):
    try:
        if await check_throttle(message.from_user.id, 'send', 600):
            await message.answer('🔍 Обрабатываю ссылку...')
            return
        url = message.text.strip()
        user_id = message.from_user.id

        # Кидаем задачу в Celery
        parse_youtube_formats.delay(user_id, url)
        await message.reply("🔍 Обрабатываю ссылку... Появятся кнопки с форматами, как только всё будет готово!")

    except Exception as e:
        logging.exception(f"Ошибка при получении форматов: {e}")
        await message.reply(
            "❌ Произошла ошибка при загрузке видео.\n\n"
            "Пожалуйста, отправьте **прямую ссылку на видео**, например:\n"
            "`https://youtu.be/VIDEO_ID` или `https://www.youtube.com/watch?v=VIDEO_ID`\n\n"
            "⚠️ Ссылки на плейлисты, каналы или сборники не поддерживаются."
        )



@router.callback_query(F.data.startswith("dl|"))
async def on_download_click(callback: CallbackQuery, bot: Bot):
    user_id = callback.from_user.id


    try:
        if not await can_download(user_id):
            await callback.message.answer("❗️Превышен лимит скачиваний на сегодня.")
            return
        if await check_throttle(callback.from_user.id, 'dl', 600):
            await callback.message.answer("⏳ Уже скачивается. Подожди завершения.")
            return


        _, format_id = callback.data.split("|")
        redis_key = f"yt:{callback.from_user.id}:{format_id}"
        url_bytes = await redis_client.get(redis_key)
        url = url_bytes.decode() if url_bytes else None



        if not url:
            await callback.message.answer("❌ Ссылка устарела или не найдена.")
            return
        print(url)
        task = download_and_upload_video.delay(url, callback.data, user_id)

        await callback.message.answer("📥 Скачиваю...\n\nЯ пришлю ссылку, как только оно будет готово.")

        await DataBase.increment_sent_links(user_id)


    except Exception as e:
        logging.exception("Ошибка скачивания:")
        await callback.message.answer("❌ Не удалось скачать выбранный формат.")

