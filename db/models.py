from datetime import datetime
from sqlalchemy import Column, DateTime, Integer, String, BigInteger, ForeignKey, JSON, Boolean, Enum, Text, Table, \
    UniqueConstraint, ARRAY
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class Users(Base):
    """
    Модель пользователя в системе
    """
    __tablename__ = 'users'
    
    # Основные поля
    user_id = Column(BigInteger, primary_key=True, index=True)
    user_name = Column(String, nullable=True)
    name = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), default=datetime.now)

    status = Column(Enum('active', 'blocked', 'deleted', name='message_type_enum'), nullable=False, default='active')
    sent_links = Column(Integer, nullable=False, default=0)
    download_limit = Column(Integer, default=3)  # лимит по умолчанию

class Downloads(Base):
    __tablename__ = "downloads"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, nullable=False, index=True)
    downloaded_at = Column(DateTime(timezone=True), nullable=False, default=datetime.now)
    url_orig = Column(String)


class Logger(Base):
    """
    Модель для логирования действий пользователей
    """
    __tablename__ = 'logger'

    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime(timezone=True), default=datetime.now)
    user_id = Column(BigInteger)
    user_name = Column(String, nullable=True)
    type = Column(String)
    action = Column(String)

