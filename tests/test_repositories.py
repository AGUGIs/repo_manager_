from datetime import date

import bootstrap  # noqa: F401

from models import Project, Repository, User
from models.repositories import (
    add_repository,
    find_repository,
    short_url,
    visibility_text,
)


def _project() -> Project:
    owner = User(1, 'kirill', 'Кирилл Челышев', 'kirill@edu.mirea.ru')
    return Project(1, 'Курсовой дневник', owner, date(2026, 2, 3))


def test_repository_creation():
    project = _project()
    repo = Repository(
        1,
        project,
        'course-notes',
        'https://gitlab.local/course-notes.git',
        False,
    )
    assert repo.id == 1
    assert repo.name == 'course-notes'
    assert repo.project is project
    assert repo.visibility_text() == 'Репозиторий открыт для просмотра'


def test_add_repository():
    repositories: list[Repository] = []
    add_repository(
        repositories,
        _project(),
        'course-notes',
        'https://gitlab.local/course-notes.git',
        False,
    )
    assert len(repositories) == 1
    assert repositories[0].name == 'course-notes'


def test_find_repository():
    repositories: list[Repository] = []
    add_repository(
        repositories,
        _project(),
        'course-notes',
        'https://gitlab.local/course-notes.git',
        False,
    )
    assert find_repository(repositories, 'course')


def test_visibility_text():
    assert visibility_text(True) == 'Доступ к репозиторию ограничен'
    assert visibility_text(False) == 'Репозиторий открыт для просмотра'


def test_short_url():
    url = 'https://gitlab.local/course-notes.git'
    assert short_url(url) == 'https://gi***otes.git'
    assert short_url('short') == 'скрыто'


if __name__ == '__main__':
    import pytest
    pytest.main([__file__])
