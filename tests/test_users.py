import bootstrap  # noqa: F401

from models import User
from models.users import add_user, find_user, get_user_by_username


def test_user_creation():
    user = User(1, 'kirill', 'Кирилл Челышев', 'kirill@edu.mirea.ru')
    assert user.id == 1
    assert user.username == 'kirill'
    assert user.full_name == 'Кирилл Челышев'
    assert user.email == 'kirill@edu.mirea.ru'


def test_user_str():
    user = User(1, 'kirill', 'Кирилл Челышев', 'kirill@edu.mirea.ru')
    assert str(user) == 'Кирилл Челышев (kirill)'


def test_user_from_data():
    user = User.from_data({
        'id': 1,
        'username': 'kirill',
        'full_name': 'Кирилл Челышев',
        'email': 'kirill@edu.mirea.ru',
    })
    assert user.username == 'kirill'


def test_add_user():
    users: list[User] = []
    user = add_user(users, 'kirill', 'Кирилл Челышев')
    assert len(users) == 1
    assert user.username == 'kirill'


def test_find_user():
    users: list[User] = []
    add_user(users, 'kirill', 'Кирилл Челышев')
    assert find_user(users, 'челышев')
    assert get_user_by_username(users, 'kirill') is not None


def test_duplicate_username_forbidden():
    users: list[User] = []
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
