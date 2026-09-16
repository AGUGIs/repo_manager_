"""Загрузка и сохранение данных проекта в JSON."""

import json
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent / 'data'


def _resolve(filename: str) -> Path:
    """Вернуть абсолютный путь к файлу данных."""
    path = Path(filename)
    if path.is_absolute():
        return path
    return DATA_DIR / filename


def _load_list(filename: str) -> list[dict]:
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
    return data


def _save_list(filename: str, records: list[dict]) -> None:
    """Записать список словарей в JSON-файл."""
    path = _resolve(filename)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, 'w', encoding='utf-8') as file:
        json.dump(records, file, ensure_ascii=False, indent=2)


def _to_dict(records: list[dict]) -> dict[int, dict]:
    """Преобразовать список записей в словарь по полю id."""
    return {item['id']: item for item in records}


def load_projects(filename: str = 'projects.json') -> dict[int, dict]:
    """Загрузить проекты из JSON-файла."""
    return _to_dict(_load_list(filename))


def save_projects(
    projects: dict[int, dict],
    filename: str = 'projects.json',
) -> None:
    """Сохранить проекты в JSON-файл."""
    _save_list(filename, list(projects.values()))


def load_repositories(
    filename: str = 'repositories.json',
) -> dict[int, dict]:
    """Загрузить репозитории из JSON-файла."""
    return _to_dict(_load_list(filename))


def save_repositories(
    repositories: dict[int, dict],
    filename: str = 'repositories.json',
) -> None:
    """Сохранить репозитории в JSON-файл."""
    _save_list(filename, list(repositories.values()))


def load_members(filename: str = 'members.json') -> list[dict]:
    """Загрузить участников из JSON-файла."""
    return _load_list(filename)


def save_members(
    members: list[dict],
    filename: str = 'members.json',
) -> None:
    """Сохранить участников в JSON-файл."""
    _save_list(filename, members)
