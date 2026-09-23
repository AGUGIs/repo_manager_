from datetime import date

import bootstrap  # noqa: F401

from models import Member, Project, Repository, User
from models.members import (
    add_member,
    can_push,
    get_access_status,
    is_member_assigned,
    revoke_member,
)


def _repo() -> Repository:
    owner = User(1, 'kirill', 'Кирилл Челышев', 'kirill@edu.mirea.ru')
    project = Project(1, 'Курсовой дневник', owner, date(2026, 2, 3))
    return Repository(
        1,
        project,
        'course-notes',
        'https://gitlab.local/course-notes.git',
        False,
    )


def test_can_push():
    assert can_push('owner')
    assert can_push('maintainer')
    assert not can_push('developer')


def test_get_access_status():
    text = get_access_status(True)
    assert text == 'Участник может выполнять push.'


def test_member_creation():
    repo = _repo()
    user = repo.project.owner
    member = Member(1, repo, user, 'maintainer')
    assert member.repository is repo
    assert member.user is user
    assert member.can_push()
    assert not member.is_revoked


def test_member_revoke():
    repo = _repo()
    member = Member(1, repo, repo.project.owner, 'maintainer')
    member.revoke()
    assert member.is_revoked
    assert not member.can_push()


def test_duplicate_member_forbidden():
    members: list[Member] = []
    repo = _repo()
    user = repo.project.owner
    add_member(members, repo, user, 'maintainer')
    assert is_member_assigned(members, repo, user)
    try:
        add_member(members, repo, user, 'owner')
        raised = False
    except ValueError:
        raised = True
    assert raised


def test_member_can_be_added_after_revoke():
    members: list[Member] = []
    repo = _repo()
    user = repo.project.owner
    add_member(members, repo, user, 'maintainer')
    assert revoke_member(members, 1)
    assert not is_member_assigned(members, repo, user)
    add_member(members, repo, user, 'developer')
    assert is_member_assigned(members, repo, user)
    assert len(members) == 2


if __name__ == '__main__':
    import pytest
    pytest.main([__file__])
