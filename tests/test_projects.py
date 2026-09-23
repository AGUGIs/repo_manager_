from datetime import date

import bootstrap  # noqa: F401

from models import Project, User
from models.projects import add_project, days_since_create, find_project


def _owner() -> User:
    return User(1, 'kirill', 'Кирилл Челышев', 'kirill@edu.mirea.ru')


def test_project_creation():
    owner = _owner()
    project = Project(1, 'Курсовой дневник', owner, date(2026, 2, 3))
    assert project.id == 1
    assert project.title == 'Курсовой дневник'
    assert project.owner is owner


def test_add_project():
    projects: list[Project] = []
    add_project(projects, 'Курсовой дневник', _owner(), date(2026, 2, 3))
    assert len(projects) == 1
    assert projects[0].title == 'Курсовой дневник'


def test_find_project():
    projects: list[Project] = []
    add_project(projects, 'Курсовой дневник', _owner(), date(2026, 2, 3))
    assert find_project(projects, 'курсовой')


def test_days_since_create():
    start = date(2026, 2, 3)
    current = date(2026, 9, 10)
    assert days_since_create(start, current) == 219


def test_project_days_since():
    project = Project(1, 'Курсовой дневник', _owner(), date(2026, 2, 3))
    assert project.days_since(date(2026, 9, 10)) == 219


if __name__ == '__main__':
    import pytest
    pytest.main([__file__])
