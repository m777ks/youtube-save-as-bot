# YouTube Downloader Bot

Telegram бот для скачивания видео с YouTube с возможностью выбора качества и формата.

## 🚀 Возможности

- 📥 Скачивание видео с YouTube по прямой ссылке
- 🎯 Выбор качества видео (различные форматы и разрешения)
- 💾 Загрузка файлов в S3 хранилище
- 📊 Административная панель для управления пользователями
- 🔄 Асинхронная обработка через Celery
- 📈 Система лимитов и ограничений
- 🗄️ База данных PostgreSQL для хранения статистики
- 🔄 Redis для кэширования и очередей

## 🏗️ Архитектура

Проект состоит из нескольких компонентов:

- **Telegram Bot** (`bot.py`) - основной бот на aiogram
- **Celery Worker** (`celery_app/`) - асинхронная обработка задач
- **Admin Panel** (`admin_panel/`) - Django приложение для администрирования
- **Database** (`db/`) - модели и ORM для PostgreSQL
- **Scheduler** (`scheduler/`) - планировщик задач
- **S3 Client** (`s3/`) - интеграция с S3 хранилищем

## 🛠️ Технологии

- **Python 3.11+**
- **aiogram 3.20+** - Telegram Bot API
- **Celery** - асинхронная обработка задач
- **Django** - административная панель
- **PostgreSQL** - основная база данных
- **Redis** - кэширование и очереди
- **SQLAlchemy** - ORM
- **yt-dlp** - скачивание YouTube видео
- **boto3** - интеграция с AWS S3
- **Docker & Docker Compose** - контейнеризация

## 📋 Требования

- Python 3.11+
- Docker и Docker Compose
- PostgreSQL
- Redis
- S3 совместимое хранилище

## ⚙️ Установка и настройка

### 1. Клонирование репозитория

```bash
git clone <repository-url>
cd youtube_downloader
```

### 2. Настройка переменных окружения

Создайте файл `.env` на основе примера:

```env
# Telegram Bot
BOT_TOKEN=your_bot_token
ADMIN_IDS=123456789,987654321
CHANNEL_ID_1=-1001234567890
CHANNEL_ID_2=-1009876543210
BOT_USERNAME=your_bot_username

# Database
POSTGRES_HOST=db
POSTGRES_PORT=5432
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your_password
POSTGRES_DB=youtube_downloader

# Redis
REDIS_HOST=redis
REDIS_PORT=6379
REDIS_PASSWORD=your_redis_password

# S3 Storage
S3_ACCESS_KEY_ID=your_access_key
S3_ACCESS_KEY_SECRET=your_secret_key
S3_ENDPOINT_URL=https://your-s3-endpoint.com
S3_BUCKET_NAME=your-bucket-name

# Django Admin
DJANGO_SUPERUSER_USERNAME=admin
DJANGO_SUPERUSER_PASSWORD=adminpass
```

### 3. Запуск с Docker Compose

```bash
# Запуск всех сервисов
docker-compose up -d

# Просмотр логов
docker-compose logs -f

# Остановка
docker-compose down
```


## 🚀 Использование

### Для пользователей

1. Найдите бота в Telegram по username
2. Отправьте команду `/start`
3. Отправьте ссылку на YouTube видео
4. Выберите желаемое качество из предложенных вариантов
5. Дождитесь завершения загрузки и получите ссылку на файл

### Для администраторов

1. Откройте административную панель: `http://localhost:8000/admin`
2. Войдите с учетными данными суперпользователя
3. Управляйте пользователями, просматривайте статистику и логи

## 📁 Структура проекта

```
youtube_downloader/
├── bot.py                 # Основной файл бота
├── handlers.py            # Обработчики сообщений
├── celery_app/           # Celery задачи
│   └── tasks.py
├── admin_panel/          # Django административная панель
│   ├── manage.py
│   └── admin_panel/
├── db/                   # База данных
│   ├── ORM.py           # ORM модели
│   ├── models.py        # SQLAlchemy модели
│   └── alembic/         # Миграции
├── config_data/          # Конфигурация
│   └── config.py
├── scheduler/            # Планировщик задач
├── sender/              # Отправка сообщений
├── utils/               # Утилиты
├── middlewares/         # Промежуточное ПО
├── redis_client/        # Redis клиент
├── s3/                  # S3 интеграция
├── downloads/           # Временные файлы
├── docker-compose.yml   # Docker конфигурация
├── Dockerfile          # Docker образ
├── start.sh            # Скрипт запуска
└── pyproject.toml      # Зависимости проекта
```

## 🔧 Конфигурация

### Лимиты и ограничения

- Ограничение на количество скачиваний в день
- Throttling для предотвращения спама
- Проверка размера файлов

### S3 настройки

- Автоматическая загрузка файлов в S3
- Организация файлов по пользователям
- Временные ссылки для скачивания

## 📊 Мониторинг

- Логирование всех действий пользователей
- Статистика скачиваний
- Мониторинг через административную панель
- Health checks для всех сервисов

## 🔒 Безопасность

- Валидация URL перед обработкой
- Ограничение доступа к административной панели
- Безопасное хранение конфигурации в переменных окружения
- Защита от DDoS через throttling

## 🤝 Поддержка

Если у вас возникли вопросы или проблемы:

1. Проверьте логи: `docker-compose logs -f`
2. Убедитесь, что все переменные окружения настроены правильно
3. Проверьте подключение к базе данных и Redis
4. Обратитесь к администратору: @Raymond_send

## 📝 Лицензия

Этот проект распространяется под лицензией MIT.

## 🚀 Разработка

### Добавление новых функций

1. Создайте новую ветку: `git checkout -b feature/new-feature`
2. Внесите изменения
3. Добавьте тесты
4. Создайте Pull Request


---

**Примечание**: Убедитесь, что у вас есть все необходимые права для скачивания контента с YouTube в соответствии с их условиями использования.
