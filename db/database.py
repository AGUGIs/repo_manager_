"""Подключение к SQLite, применение схемы и именованные SELECT."""
from contextlib import closing
from functools import lru_cache
from pathlib import Path
import re
import sqlite3

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / 'data' / 'repo_manager.sqlite'


def get_connection(path=None, *, readonly=False):
    """Включить внешние ключи и доступ к значениям по именам столбцов."""
    path = Path(path if path is not None else DB_PATH).resolve()
    target = path.as_uri() + '?mode=ro' if readonly else str(path)
    connection = sqlite3.connect(target, uri=readonly)
    connection.row_factory = sqlite3.Row
    connection.execute('PRAGMA foreign_keys = ON')
    return connection


def initialize(path=None):
    """Создать таблицы и индексы, сохранив существующие данные."""
    target = Path(path if path is not None else DB_PATH)
    target.parent.mkdir(parents=True, exist_ok=True)
    schema = (BASE_DIR / 'sql' / 'schema.sql').read_text(encoding='utf-8')
    with closing(get_connection(target)) as connection:
        connection.executescript(schema)


@lru_cache(maxsize=1)
def queries():
    """Прочитать SQL из файла; имена запроса задаёт код, не пользователь."""
    text = (BASE_DIR / 'sql' / 'queries.sql').read_text(encoding='utf-8')
    parts = re.split(r'^-- name: (\w+)\s*$', text, flags=re.MULTILINE)
    return dict(zip(parts[1::2], parts[2::2]))


def fetch_all(name, parameters=None):
    """Выполнить SELECT с параметрами и обязательно закрыть соединение."""
    with closing(get_connection(readonly=True)) as connection:
        return connection.execute(queries()[name], parameters or {}).fetchall()


def fetch_one(name, parameters=None):
    """Вернуть первую именованную строку или None."""
    with closing(get_connection(readonly=True)) as connection:
        return connection.execute(queries()[name], parameters or {}).fetchone()


if __name__ == '__main__':
    initialize()
    print(f'Схема базы данных готова: {DB_PATH}')
