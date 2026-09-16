"""Функции для работы с участниками репозиториев."""


def can_push(role: str) -> bool:
    """Проверяет, может ли участник отправлять изменения."""
    if role == 'owner':
        return True
    if role == 'maintainer':
        return True
    return False


def get_access_status(has_push: bool) -> str:
    """Вернуть текстовый статус права на push.

    Функция продолжает сценарий ПР1: по флагу доступности
    формируется сообщение для пользователя.
    """
    if has_push:
        return 'Участник может выполнять push.'
    return 'Push для этой роли запрещён.'


def is_member_assigned(
    members: list[dict],
    repo_id: int,
    username: str,
) -> bool:
    """Проверить, добавлен ли участник в репозиторий."""
    for member in members:
        same_repo = member['repo_id'] == repo_id
        same_user = member['username'] == username
        if same_repo and same_user:
            return True
    return False


def add_member(
    members: list[dict],
    repo_id: int,
    username: str,
    role: str,
) -> dict:
    """Добавить участника в список members.

    Raises:
        ValueError: если участник уже состоит в репозитории.
    """
    if is_member_assigned(members, repo_id, username):
        raise ValueError('Участник уже добавлен в репозиторий')
    member_id = max((item['id'] for item in members), default=0) + 1
    member = {
        'id': member_id,
        'repo_id': repo_id,
        'username': username,
        'role': role,
    }
    members.append(member)
    return member


def remove_member(members: list[dict], member_id: int) -> bool:
    """Удалить участника по идентификатору.

    Returns:
        True, если запись найдена и удалена, иначе False.
    """
    for index, member in enumerate(members):
        if member['id'] == member_id:
            del members[index]
            return True
    return False


def get_members_stats(members: list[dict]) -> dict[str, int]:
    """Посчитать количество участников по ролям.

    Returns:
        Словарь вида {'owner': 1, 'maintainer': 2, ...}.
    """
    stats: dict[str, int] = {}
    for member in members:
        role = member['role']
        stats[role] = stats.get(role, 0) + 1
    return stats
