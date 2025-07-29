import logging
import random
from datetime import datetime, timedelta, timezone

from db.database import *
from db.models import Logger, Users, Downloads
from sqlalchemy.future import select
from sqlalchemy import update, delete, func
from sqlalchemy.exc import IntegrityError
from config_data.config import ConfigEnv, load_config

config: ConfigEnv = load_config()

# Инициализируем логгер
logger = logging.getLogger(__name__)


class LoggerORM:

    @staticmethod
    async def create_log(user_id, user_name, action, type):
        """
        Создание лога в базе данных
        """
        async with session_factory_async() as session:
            new_log = Logger(user_id=user_id, user_name=user_name, action=action, type=type)
            session.add(new_log)
            await session.commit()

class SenderORM:
    @staticmethod
    async def get_all_user_ids_active():
        """
        Получает список всех ID активных пользователей из базы данных.
        :return: Список ID пользователей со статусом 'active'.
        """
        async with session_factory_async() as session:
            try:
                query = select(Users.user_id).where(Users.status == "active")
                result = await session.execute(query)
                user_ids = result.scalars().all()
                return user_ids
            except Exception as e:
                logger.error(f"Ошибка при получении ID активных пользователей: {e}")
                return []

    @staticmethod
    async def update_user_status(user_id: int, new_status: str) -> bool:
        """
        Обновляет статус пользователя (active, blocked, deleted)
        """
        async with session_factory_async() as session:
            query = select(Users).filter(Users.user_id == user_id)
            result = await session.execute(query)
            user = result.scalar_one_or_none()

            if not user:
                logger.warning(f"[DB] Не найден пользователь для обновления статуса: {user_id}")
                return False

            user.status = new_status
            try:
                await session.commit()
                logger.info(f"[DB] Статус пользователя {user_id} обновлен на {new_status}")
                return True
            except Exception as e:
                await session.rollback()
                logger.error(f"[DB] Ошибка при обновлении статуса пользователя {user_id}: {e}")
                return False

class DataBase:
    @staticmethod
    async def insert_user(user_id: int, user_name: str):
        """Добавляет нового пользователя в БД или обновляет данные существующего"""
        async with session_factory_async() as session:
            # Проверка, существует ли пользователь
            query = select(Users).filter(Users.user_id == user_id)
            result = await session.execute(query)
            user = result.scalar_one_or_none()

            if user:
                return False
            else:
                # Если пользователь не найден, создаем нового
                user = Users(
                    user_id=user_id,
                    user_name=user_name,
                )
                session.add(user)

            # Сохраняем изменения
            try:
                await session.commit()
            except IntegrityError as e:
                logger.error(f"Error inserting user: {e}")
                await session.rollback()
                return False
            return True

    @staticmethod
    async def get_all_users():
        """Возвращает все записи из таблицы users."""
        async with session_factory_async() as session:
            try:
                query = select(Users)
                result = await session.execute(query)
                users = result.scalars().all()
                return users
            except Exception as e:
                logger.error(f"Ошибка при получении пользователей: {e}")
                return []


    @staticmethod
    async def get_user(user_id: int):
        """Получает пользователя по ID"""
        async with session_factory_async() as session:
            query = select(Users).filter(Users.user_id == user_id)
            result = await session.execute(query)
            return result.scalar_one_or_none()

    @staticmethod
    async def get_user_started_at(user_id: int) -> datetime | None:
        """
        Возвращает дату первого взаимодействия пользователя (created_at)
        """
        async with session_factory_async() as session:
            query = select(Users).where(Users.user_id == user_id)
            result = await session.execute(query)
            user = result.scalar_one_or_none()

            if user:
                return user.created_at
            else:
                logger.warning(f"[DB] Пользователь {user_id} не найден в базе")
                return None

    @staticmethod
    async def delete_user(user_id: int) -> bool:
        """
        Удаляет пользователя из базы данных по user_id.
        Возвращает True, если пользователь был удалён, иначе False.
        """
        async with session_factory_async() as session:
            try:
                query = select(Users).filter(Users.user_id == user_id)
                result = await session.execute(query)
                user = result.scalar_one_or_none()

                if not user:
                    return False

                await session.delete(user)
                await session.commit()
                return True

            except Exception as e:
                await session.rollback()
                logger.error(f"[DB] Ошибка при удалении пользователя {user_id}: {e}")
                return False



    @staticmethod
    async def increment_sent_links(user_id: int) -> bool:
        """
        Увеличивает счётчик отправленных пользователю ссылок на 1.
        """
        async with session_factory_async() as session:
            query = select(Users).filter(Users.user_id == user_id)
            result = await session.execute(query)
            user = result.scalar_one_or_none()

            if not user:
                logger.warning(f"[DB] Не найден пользователь для инкремента ссылок: {user_id}")
                return False

            user.sent_links = (user.sent_links or 0) + 1
            try:
                await session.commit()
                logger.info(f"[DB] Счётчик ссылок для {user_id} увеличен: {user.sent_links}")
                return True
            except Exception as e:
                await session.rollback()
                logger.error(f"[DB] Ошибка при увеличении счётчика ссылок {user_id}: {e}")
                return False

    @staticmethod
    async def log_download(user_id: int, url_orig: str):
        """Логирует факт скачивания файла."""
        async with session_factory_async() as session:
            download = Downloads(user_id=user_id, url_orig=url_orig)
            session.add(download)
            await session.commit()