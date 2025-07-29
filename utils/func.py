import re


def sanitize_filename(title: str) -> str:
    # Удаляем запрещённые символы для файлов: / \ : * ? " < > |
    return re.sub(r'[\\/:"*?<>|]+', "", title)

