import bootstrap  # noqa: F401

from users import (
    add_user,
    find_user,
    get_user_by_username,
)


def test_add_user():
    users: dict[int, dict] = {}
    user = add_user(users, 'kirill', 'Кирилл Челышев')
    assert len(users) == 1
    assert user['username'] == 'kirill'


def test_find_user():
    users: dict[int, dict] = {}
    add_user(users, 'kirill', 'Кирилл Челышев')
    assert find_user(users, 'челышев')
    assert get_user_by_username(users, 'kirill') is not None


def test_duplicate_username_forbidden():
    users: dict[int, dict] = {}
    add_user(users, 'kirill', 'Кирилл Челышев')
    try:
        add_user(users, 'kirill', 'Другой Кирилл')
        raised = False
    except ValueError:
        raised = True
    assert raised


if __name__ == '__main__':
    import pytest
    pytest.main([__file__])
