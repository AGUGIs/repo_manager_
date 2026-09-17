"""Загрузка и сохранение данных проекта в JSON."""

import json
from pathlib import Path
from typing import Any, cast

DATA_DIR = Path(__file__).resolve().parent / 'data'


def _resolve(filename: str) -> Path:
    """Вернуть абсолютный путь к файлу данных."""
    path = Path(filename)
    if path.is_absolute():
        return path
    return DATA_DIR / filename


def _load_list(filename: str) -> list[dict[str, Any]]:
    """Прочитать JSON-список. При ошибке вернуть пустой список."""
    path = _resolve(filename)
    try:
        with open(path, 'r', encoding='utf-8') as file:
            data = json.load(file)
    except FileNotFoundError:
        return []
    except json.JSONDecodeError:
        return []
    if not isinstance(data, list):
        return []
    return cast(list[dict[str, Any]], data)


def _save_list(filename: str, records: list[dict[str, Any]]) -> None:
    """Записать список словарей в JSON-файл."""
    path = _resolve(filename)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, 'w', encoding='utf-8') as file:
        json.dump(records, file, ensure_ascii=False, indent=2)


def _to_dict(records: list[dict[str, Any]]) -> dict[int, dict[str, Any]]:
    """Преобразовать список записей в словарь по полю id."""
    return {int(item['id']): item for item in records}


def load_projects(
    filename: str = 'projects.json',
) -> dict[int, dict[str, Any]]:
    """Загрузить проекты из JSON-файла."""
    return _to_dict(_load_list(filename))


def save_projects(
    projects: dict[int, dict[str, Any]],
    filename: str = 'projects.json',
) -> None:
    """Сохранить проекты в JSON-файл."""
    _save_list(filename, list(projects.values()))


def load_repositories(
    filename: str = 'repositories.json',
) -> dict[int, dict[str, Any]]:
    """Загрузить репозитории из JSON-файла."""
    return _to_dict(_load_list(filename))


def save_repositories(
    repositories: dict[int, dict[str, Any]],
    filename: str = 'repositories.json',
) -> None:
    """Сохранить репозитории в JSON-файл."""
    _save_list(filename, list(repositories.values()))


def load_members(filename: str = 'members.json') -> list[dict[str, Any]]:
    """Загрузить участников из JSON-файла."""
    return _load_list(filename)


def save_members(
    members: list[dict[str, Any]],
    filename: str = 'members.json',
) -> None:
    """Сохранить участников в JSON-файл."""
    _save_list(filename, members)


def load_users(filename: str = 'users.json') -> dict[int, dict[str, Any]]:
    """Загрузить пользователей из JSON-файла."""
    return _to_dict(_load_list(filename))


def save_users(
    users: dict[int, dict[str, Any]],
    filename: str = 'users.json',
) -> None:
    """Сохранить пользователей в JSON-файл."""
    _save_list(filename, list(users.values()))
