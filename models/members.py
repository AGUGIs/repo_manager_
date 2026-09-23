"""Класс Member и функции работы с коллекцией участников."""

from typing import Any

from .base import DomainEntity, next_id
from .repositories import Repository
from .users import User

WRITE_ROLES = {'owner', 'maintainer'}


class Member(DomainEntity):
    """Доступ пользователя к репозиторию с указанной ролью."""

    def __init__(
        self,
        member_id: int,
        repository: Repository,
        user: User,
        role: str,
    ) -> None:
        super().__init__(member_id)
        self.repository = repository
        self.user = user
        self.role = role
        self.is_revoked = False

    def can_push(self) -> bool:
        """Проверить, может ли участник отправлять изменения."""
        if self.is_revoked:
            return False
        return self.role in WRITE_ROLES

    def revoke(self) -> None:
        """Отозвать доступ, не удаляя запись из коллекции."""
        self.is_revoked = True

    def access_status(self) -> str:
        """Вернуть текстовый статус права на push."""
        if self.can_push():
            return 'Участник может выполнять push.'
        return 'Push для этой роли запрещён.'

    def to_dict(self) -> dict[str, Any]:
        """Преобразовать участника в данные JSON."""
        return {
            'id': self.id,
            'repo_id': self.repository.id,
            'user_id': self.user.id,
            'role': self.role,
            'is_revoked': self.is_revoked,
        }

    def __str__(self) -> str:
        state = 'отозван' if self.is_revoked else self.role
        return (
            f'{self.user} | {state} | {self.repository.name}'
        )


def can_push(role: str) -> bool:
    """Проверить роль без объекта. Оставлено для сценария ПР1."""
    if role == 'owner':
        return True
    if role == 'maintainer':
        return True
    return False


def get_access_status(has_push: bool) -> str:
    """Вернуть текстовый статус права на push. Сценарий ПР1."""
    if has_push:
        return 'Участник может выполнять push.'
    return 'Push для этой роли запрещён.'


def is_member_assigned(
    members: list[Member],
    repository: Repository,
    user: User,
) -> bool:
    """Проверить, есть ли активный доступ пользователя к репо."""
    for member in members:
        same_repo = member.repository.id == repository.id
        same_user = member.user.id == user.id
        if same_repo and same_user and not member.is_revoked:
            return True
    return False


def add_member(
    members: list[Member],
    repository: Repository,
    user: User,
    role: str,
) -> Member:
    """Создать объект Member и добавить его в коллекцию.

    Raises:
        ValueError: если активный доступ уже есть.
    """
    if is_member_assigned(members, repository, user):
        raise ValueError('Участник уже добавлен в репозиторий')
    member = Member(next_id(members), repository, user, role)
    members.append(member)
    return member


def revoke_member(members: list[Member], member_id: int) -> bool:
    """Отозвать доступ участника по идентификатору."""
    for member in members:
        if member.id == member_id and not member.is_revoked:
            member.revoke()
            return True
    return False


def get_member_by_id(
    members: list[Member],
    member_id: int,
) -> Member | None:
    """Найти участника по идентификатору."""
    for member in members:
        if member.id == member_id:
            return member
    return None


def get_members_stats(members: list[Member]) -> dict[str, int]:
    """Посчитать активных участников по ролям."""
    stats: dict[str, int] = {}
    for member in members:
        if member.is_revoked:
            continue
        stats[member.role] = stats.get(member.role, 0) + 1
    return stats


def show_members(members: list[Member]) -> None:
    """Вывести список участников."""
    print('\nУчастники:')
    if not members:
        print('Список участников пуст.')
        return
    for member in members:
        print(f'{member.id}. {member}')
