"""Базовый класс сущностей предметной области."""

from collections.abc import Sequence
from typing import Any


class DomainEntity:
    """Общая часть сущностей: идентификатор и JSON-представление."""

    def __init__(self, entity_id: int) -> None:
        self._id = entity_id

    @property
    def id(self) -> int:
        """Вернуть идентификатор сущности."""
        return self._id

    def to_dict(self) -> dict[str, Any]:
        """Преобразовать объект в данные для JSON."""
        raise NotImplementedError

    def __str__(self) -> str:
        return f'{self.__class__.__name__} #{self.id}'


def next_id(items: Sequence[DomainEntity]) -> int:
    """Вернуть следующий идентификатор для коллекции объектов."""
    return max((item.id for item in items), default=0) + 1
