"""Класс Project и функции работы с коллекцией проектов."""

from datetime import date, datetime
from typing import Any

from .base import DomainEntity, next_id
from .users import User


class Project(DomainEntity):
    """Учебный проект, которому принадлежат репозитории."""

    def __init__(
        self,
        project_id: int,
        title: str,
        owner: User,
        opened_on: date,
    ) -> None:
        super().__init__(project_id)
        self.title = title
        self.owner = owner
        self.opened_on = opened_on

    def days_since(self, current: date) -> int:
        """Считает, сколько дней прошло с создания проекта."""
        return (current - self.opened_on).days

    def matches(self, query: str) -> bool:
        """Проверить, встречается ли запрос в названии проекта."""
        return query.lower() in self.title.lower()

    def to_dict(self) -> dict[str, Any]:
        """Преобразовать проект в данные JSON."""
        return {
            'id': self.id,
            'title': self.title,
            'owner_id': self.owner.id,
            'opened_on': self.opened_on.isoformat(),
        }

    def __str__(self) -> str:
        age = self.days_since(date.today())
        return f'{self.title} | владелец: {self.owner} | {age} дн.'


def get_project_by_id(
    projects: list[Project],
    project_id: int,
) -> Project | None:
    """Найти проект по идентификатору."""
    for project in projects:
        if project.id == project_id:
            return project
    return None


def add_project(
    projects: list[Project],
    title: str,
    owner: User,
    opened_on: date,
) -> Project:
    """Создать объект Project и добавить его в коллекцию."""
    project = Project(next_id(projects), title, owner, opened_on)
    projects.append(project)
    return project


def find_project(projects: list[Project], query: str) -> list[Project]:
    """Найти проекты по подстроке названия."""
    return [project for project in projects if project.matches(query)]


def sort_projects(projects: list[Project]) -> list[Project]:
    """Отсортировать проекты по дате создания."""
    return sorted(projects, key=lambda item: item.opened_on)


def days_since_create(start: date, current: date) -> int:
    """Считает разницу дат. Оставлено для сценария ПР1."""
    return (current - start).days


def show_projects(projects: list[Project]) -> None:
    """Вывести список учебных проектов."""
    print('\nПроекты:')
    if not projects:
        print('Список проектов пуст.')
        return
    for project in sort_projects(projects):
        print(f'{project.id}. {project}')


def parse_opened_on(value: str) -> date:
    """Преобразовать дату из JSON в объект date."""
    return datetime.strptime(value, '%Y-%m-%d').date()
