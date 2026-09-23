"""Класс Repository и функции работы с коллекцией репозиториев."""

from collections.abc import Iterator
from typing import Any

from .base import DomainEntity, next_id
from .projects import Project


class Repository(DomainEntity):
    """Git-репозиторий учебного проекта."""

    def __init__(
        self,
        repo_id: int,
        project: Project,
        name: str,
        clone_url: str,
        private: bool,
    ) -> None:
        super().__init__(repo_id)
        self.project = project
        self.name = name
        self.clone_url = clone_url
        self._private = private

    @property
    def private(self) -> bool:
        """Вернуть признак закрытого доступа."""
        return self._private

    def visibility_text(self) -> str:
        """Вернуть подпись режима доступа к репозиторию."""
        if self.private:
            return 'Доступ к репозиторию ограничен'
        return 'Репозиторий открыт для просмотра'

    def masked_url(self) -> str:
        """Сократить адрес клонирования при печати."""
        if len(self.clone_url) < 18:
            return 'скрыто'
        return self.clone_url[0:10] + '***' + self.clone_url[-8:]

    def matches(self, query: str) -> bool:
        """Проверить, встречается ли запрос в имени репозитория."""
        return query.lower() in self.name.lower()

    def to_dict(self) -> dict[str, Any]:
        """Преобразовать репозиторий в данные JSON."""
        return {
            'id': self.id,
            'project_id': self.project.id,
            'name': self.name,
            'clone_url': self.clone_url,
            'private': self.private,
        }

    def __str__(self) -> str:
        return (
            f'{self.name} | {self.project.title} | '
            f'{self.visibility_text()} | {self.masked_url()}'
        )


def get_repository_by_id(
    repositories: list[Repository],
    repo_id: int,
) -> Repository | None:
    """Найти репозиторий по идентификатору."""
    for repo in repositories:
        if repo.id == repo_id:
            return repo
    return None


def add_repository(
    repositories: list[Repository],
    project: Project,
    name: str,
    clone_url: str,
    private: bool,
) -> Repository:
    """Создать объект Repository и добавить его в коллекцию."""
    repo = Repository(
        next_id(repositories),
        project,
        name,
        clone_url,
        private,
    )
    repositories.append(repo)
    return repo


def find_repository(
    repositories: list[Repository],
    query: str,
) -> list[Repository]:
    """Найти репозитории по подстроке названия."""
    return [repo for repo in repositories if repo.matches(query)]


def iter_repos_by_visibility(
    repositories: list[Repository],
    private: bool,
) -> Iterator[Repository]:
    """Генератор репозиториев с заданным режимом доступа."""
    for repo in repositories:
        if repo.private is private:
            yield repo


def filter_repos_by_visibility(
    repositories: list[Repository],
    private: bool,
) -> list[Repository]:
    """Отобрать репозитории по режиму доступа."""
    return list(iter_repos_by_visibility(repositories, private))


def sort_repos(repositories: list[Repository]) -> list[Repository]:
    """Отсортировать репозитории по имени."""
    return sorted(repositories, key=lambda item: item.name.lower())


def visibility_text(private_flag: bool) -> str:
    """Подпись доступа. Оставлено для сценария ПР1."""
    if private_flag:
        return 'Доступ к репозиторию ограничен'
    return 'Репозиторий открыт для просмотра'


def short_url(url: str) -> str:
    """Сокращает адрес клонирования. Оставлено для сценария ПР1."""
    if len(url) < 18:
        return 'скрыто'
    return url[0:10] + '***' + url[-8:]


def show_repositories(repositories: list[Repository]) -> None:
    """Вывести список репозиториев."""
    print('\nРепозитории:')
    if not repositories:
        print('Список репозиториев пуст.')
        return
    for repo in sort_repos(repositories):
        print(f'{repo.id}. {repo}')
