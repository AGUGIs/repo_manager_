"""Функции для работы с пользователями."""

from typing import Any


def add_user(
    users: dict[int, dict[str, Any]],
    username: str,
    full_name: str,
) -> dict[str, Any]:
    """Добавить пользователя в словарь users.

    Raises:
        ValueError: если логин уже занят.
    """
    if get_user_by_username(users, username) is not None:
        raise ValueError('Пользователь с таким логином уже есть')
    user_id = max(users.keys(), default=0) + 1
    user = {
        'id': user_id,
        'username': username,
        'full_name': full_name,
    }
    users[user_id] = user
    return user


def get_user(
    users: dict[int, dict[str, Any]],
    user_id: int,
) -> dict[str, Any] | None:
    """Вернуть пользователя по идентификатору."""
    return users.get(user_id)


def get_user_by_username(
    users: dict[int, dict[str, Any]],
    username: str,
) -> dict[str, Any] | None:
    """Вернуть пользователя по логину."""
    for user in users.values():
        if user['username'] == username:
            return user
    return None


def find_user(
    users: dict[int, dict[str, Any]],
    query: str,
) -> list[dict[str, Any]]:
    """Найти пользователей по логину или ФИО."""
    query_lower = query.lower()
    found: list[dict[str, Any]] = []
    for user in users.values():
        username = user['username'].lower()
        full_name = user['full_name'].lower()
        if query_lower in username or query_lower in full_name:
            found.append(user)
    return found


def sort_users(
    users: dict[int, dict[str, Any]],
) -> list[dict[str, Any]]:
    """Отсортировать пользователей по ФИО."""
    return sorted(
        users.values(),
        key=lambda item: item['full_name'].lower(),
    )
