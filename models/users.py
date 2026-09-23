"""Класс User и функции работы с коллекцией пользователей."""

from typing import Any

from .base import DomainEntity, next_id


class User(DomainEntity):
    """Пользователь системы управления репозиториями."""

    def __init__(
        self,
        user_id: int,
        username: str,
        full_name: str,
        email: str,
    ) -> None:
        super().__init__(user_id)
        self.username = username
        self.full_name = full_name
        self.email = email

    @classmethod
    def from_data(cls, data: dict[str, Any]) -> 'User':
        """Создать пользователя из словаря JSON."""
        return cls(
            user_id=int(data['id']),
            username=str(data['username']),
            full_name=str(data['full_name']),
            email=str(data.get('email', '')),
        )

    @staticmethod
    def validate_username(username: str) -> bool:
        """Проверить, что логин не пустой."""
        return bool(username.strip())

    def matches(self, query: str) -> bool:
        """Проверить, подходит ли пользователь под поисковый запрос."""
        text = query.lower()
        return text in self.username.lower() or text in self.full_name.lower()

    def to_dict(self) -> dict[str, Any]:
        """Преобразовать пользователя в данные JSON."""
        return {
            'id': self.id,
            'username': self.username,
            'full_name': self.full_name,
            'email': self.email,
        }

    def __str__(self) -> str:
        return f'{self.full_name} ({self.username})'


def get_user_by_id(users: list[User], user_id: int) -> User | None:
    """Найти пользователя по идентификатору."""
    for user in users:
        if user.id == user_id:
            return user
    return None


def get_user_by_username(users: list[User], username: str) -> User | None:
    """Найти пользователя по логину."""
    for user in users:
        if user.username == username:
            return user
    return None


def add_user(
    users: list[User],
    username: str,
    full_name: str,
    email: str = '',
) -> User:
    """Создать объект User и добавить его в коллекцию.

    Raises:
        ValueError: если логин пустой или уже занят.
    """
    if not User.validate_username(username):
        raise ValueError('Логин не может быть пустым')
    if get_user_by_username(users, username) is not None:
        raise ValueError('Пользователь с таким логином уже есть')
    user = User(next_id(users), username, full_name, email)
    users.append(user)
    return user


def find_user(users: list[User], query: str) -> list[User]:
    """Найти пользователей по логину или ФИО."""
    return [user for user in users if user.matches(query)]


def sort_users(users: list[User]) -> list[User]:
    """Отсортировать пользователей по ФИО."""
    return sorted(users, key=lambda item: item.full_name.lower())


def show_users(users: list[User]) -> None:
    """Вывести список пользователей."""
    print('\nПользователи:')
    if not users:
        print('Список пользователей пуст.')
        return
    for user in sort_users(users):
        print(f'{user.id}. {user}')
