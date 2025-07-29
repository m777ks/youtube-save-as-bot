import asyncio
import logging
import limited_aiogram

from aiogram import Dispatcher
from aiogram.fsm.storage.redis import RedisStorage

import handlers
from config_data.config import ConfigEnv, load_config
from redis_client.client_redis import redis_client
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from scheduler.check_s3 import check_s3_results, check_formats_ready
from sender import sender
from utils.main_menu import set_main_menu

config: ConfigEnv = load_config()

# Инициализируем логгер
logger = logging.getLogger(__name__)

bot = limited_aiogram.LimitedBot(token=config.tg_bot.token)

storage = RedisStorage(redis=redis_client)

scheduler = AsyncIOScheduler(timezone='Asia/Tbilisi')

async def main():
    # await start_http_server()

    scheduler.start()

    scheduler.add_job(check_s3_results,
                      trigger="interval",
                      seconds=10,
                      kwargs={'bot': bot,},
                      id='check_s3',
                      max_instances=1,
                      coalesce=True)

    scheduler.add_job(check_formats_ready, "interval", seconds=2, args=[bot])

    # Конфигурируем логирование
    logging.basicConfig(
        level=logging.INFO,
        format='%(filename)s:%(lineno)d #%(levelname)-8s '
               '[%(asctime)s] - %(name)s - %(message)s')

    # Выводим в консоль информацию о начале запуска бота
    logger.info('Starting bot')

    dp = Dispatcher(bot=bot, storage=storage)


    dp.include_router(handlers.router)
    dp.include_router(sender.router)


    # Настраиваем главное меню бота
    await set_main_menu(bot)

    # Пропускаем накопившиеся апдейты и запускаем polling
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())