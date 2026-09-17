import bootstrap  # noqa: F401

from members import (
    add_member,
    can_push,
    get_access_status,
    is_member_assigned,
    remove_member,
)


def test_can_push():
    assert can_push('owner')
    assert can_push('maintainer')
    assert not can_push('developer')


def test_get_access_status():
    text = get_access_status(True)
    assert text == 'Участник может выполнять push.'


def test_duplicate_member_forbidden():
    members: list[dict] = []
    add_member(members, 1, 1, 'maintainer')
    assert is_member_assigned(members, 1, 1)
    try:
        add_member(members, 1, 1, 'owner')
        raised = False
    except ValueError:
        raised = True
    assert raised


def test_remove_member():
    members: list[dict] = []
    add_member(members, 1, 1, 'maintainer')
    assert remove_member(members, 1)
    assert members == []


if __name__ == '__main__':
    import pytest
    pytest.main([__file__])
