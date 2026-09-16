from datetime import date

import bootstrap  # noqa: F401

from projects import add_project, days_since_create, find_project


def test_add_project():
    projects = {}
    add_project(
        projects,
        'Курсовой дневник',
        'Кирилл Челышев',
        date(2026, 2, 3),
    )
    assert len(projects) == 1
    assert projects[1]['title'] == 'Курсовой дневник'


def test_find_project():
    projects = {}
    add_project(
        projects,
        'Курсовой дневник',
        'Кирилл Челышев',
        date(2026, 2, 3),
    )
    assert find_project(projects, 'курсовой')


def test_days_since_create():
    start = date(2026, 2, 3)
    current = date(2026, 9, 10)
    assert days_since_create(start, current) == 219


if __name__ == '__main__':
    import pytest
    pytest.main([__file__])
