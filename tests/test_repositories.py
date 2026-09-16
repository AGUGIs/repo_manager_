import bootstrap  # noqa: F401

from repositories import (
    add_repository,
    find_repository,
    short_url,
    visibility_text,
)


def test_add_repository():
    repositories = {}
    add_repository(
        repositories,
        1,
        'course-notes',
        'https://gitlab.local/course-notes.git',
        False,
    )
    assert len(repositories) == 1
    assert repositories[1]['name'] == 'course-notes'


def test_find_repository():
    repositories = {}
    add_repository(
        repositories,
        1,
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
