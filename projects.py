"""Функции для работы с учебными проектами."""

from datetime import date
from typing import Any


def add_project(
    projects: dict[int, dict[str, Any]],
    title: str,
    owner_id: int,
    opened_on: date,
) -> None:
    """Добавить проект в словарь projects.

    Args:
        projects: словарь проектов, ключ — идентификатор.
        title: название учебного проекта.
        owner_id: идентификатор пользователя-владельца.
        opened_on: дата создания проекта.
    """
    project_id = max(projects.keys(), default=0) + 1
    projects[project_id] = {
        'id': project_id,
        'title': title,
        'owner_id': owner_id,
        'opened_on': opened_on.isoformat(),
    }


def find_project(
    projects: dict[int, dict[str, Any]],
    query: str,
) -> list[dict[str, Any]]:
    """Найти проекты по подстроке названия.

    Args:
        projects: словарь проектов.
        query: фрагмент названия.

    Returns:
        Список проектов, в названии которых встречается query.
    """
    query_lower = query.lower()
    found: list[dict[str, Any]] = []
    for project in projects.values():
        if query_lower in project['title'].lower():
            found.append(project)
    return found


def days_since_create(start: date, current: date) -> int:
    """Считает, сколько дней прошло с создания проекта."""
    delta = current - start
    return delta.days


def sort_projects(
    projects: dict[int, dict[str, Any]],
) -> list[dict[str, Any]]:
    """Отсортировать проекты по дате создания.

    Returns:
        Список проектов, упорядоченный по возрастанию даты.
    """
    return sorted(
        projects.values(),
        key=lambda item: item['opened_on'],
    )
