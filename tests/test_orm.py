"""Миграции, перенос, CRUD, целостность и совместные ORM-сценарии ПР9."""
from contextlib import closing
import sqlite3
from urllib.parse import parse_qs, urlsplit
import re

from django.core.management import call_command
from django.db import connection, IntegrityError, transaction
from django.db.models.deletion import ProtectedError
from django.test.utils import CaptureQueriesContext
import pytest

from access.models import Member, User
from catalog.management.commands.import_pr7 import import_source
from catalog.models import Project, Repository
from db import database


def clear_target():
    Member.objects.all().delete()
    Repository.objects.all().delete()
    Project.objects.all().delete()
    User.objects.all().delete()


def test_crud_and_relationships(web):
    owner = User.objects.get(pk=7)
    project = owner.projects.get(pk=11)
    repo = project.repositories.create(
        name='new', clone_url='https://example.org/new', private=False)
    member = repo.members.create(user=owner, role='maintainer')
    assert member.repository.project.owner == owner
    assert owner.memberships.filter(repository=repo).count() == 1
    assert member.can_push()
    member.revoke()
    member.refresh_from_db()
    assert member.is_revoked and not member.can_push()
    Repository.objects.filter(pk=repo.pk).update(name='changed')
    repo.refresh_from_db()
    assert repo.name == 'changed'
    repo.delete()
    assert not Member.objects.filter(pk=member.pk).exists()


def test_constraints_and_protection(web):
    with pytest.raises(ProtectedError):
        User.objects.get(pk=7).delete()
    with pytest.raises(ProtectedError):
        Project.objects.get(pk=11).delete()
    with pytest.raises(IntegrityError), transaction.atomic():
        Member.objects.create(repository_id=13, user_id=7, role='owner')
    Member.objects.get(pk=17).revoke()
    new = Member.objects.create(repository_id=13, user_id=7, role='owner')
    assert new.can_push()
    with pytest.raises(IntegrityError), transaction.atomic():
        User.objects.create(username='tester', full_name='Duplicate')
    with pytest.raises(IntegrityError), transaction.atomic():
        User.objects.create(username='', full_name='Empty')


def test_import_idempotent_and_source_unchanged(web):
    original = database.DB_PATH.read_bytes()
    for _ in range(2):
        assert import_source(database.DB_PATH) == {
            'User': 1, 'Project': 1, 'Repository': 1, 'Member': 2}
    assert original == database.DB_PATH.read_bytes()
    assert Member.objects.get(pk=17).repository_id == 13
    assert Project.objects.get(pk=11).owner_id == 7
    assert Member.objects.get(pk=18).is_revoked


def test_import_does_not_overwrite_edits(web):
    User.objects.filter(pk=7).update(full_name='Edited')
    with pytest.raises(ValueError, match='без изменений'):
        import_source(database.DB_PATH)
    assert User.objects.get(pk=7).full_name == 'Edited'
    assert Member.objects.count() == 2


def test_import_atomic_on_broken_relationship(web):
    clear_target()
    with closing(sqlite3.connect(database.DB_PATH)) as db:
        with db:
            db.execute('UPDATE members SET repo_id=999 WHERE id=17')
    with pytest.raises(IntegrityError):
        import_source(database.DB_PATH)
    assert User.objects.count() == 0
    assert Project.objects.count() == 0
    assert Repository.objects.count() == 0
    assert Member.objects.count() == 0


def test_import_missing_source_not_created(web, tmp_path):
    missing = tmp_path / 'missing.sqlite'
    with pytest.raises(sqlite3.OperationalError):
        import_source(missing)
    assert not missing.exists()
    assert User.objects.count() == 1


def test_schema_matches_migrations(web):
    call_command('makemigrations', check=True, dry_run=True, verbosity=0)
    with connection.cursor() as cursor:
        cursor.execute('SELECT COUNT(*) FROM django_migrations')
        assert cursor.fetchone()[0] == 3


def test_web_uses_only_orm_copy(web):
    client, folder = web
    database.DB_PATH.unlink()
    for path in folder.iterdir():
        path.unlink()
    assert client.get('/repositories/13/').status_code == 200
    assert client.get('/statistics/').context['member_summary']['total'] == 2


@pytest.mark.parametrize('url', ['/repositories/', '/repositories/search/'])
def test_filters_sort_and_pagination_together(web, url):
    client, _ = web
    for i in range(25):
        Repository.objects.create(project_id=11, name=f'lab-{i:02}',
                                  clone_url='https://example.org',
                                  private=True)
    params = {'q': 'lab', 'visibility': 'private', 'project_id': '11',
              'sort': '-name'}
    first = client.get(url, params)
    assert first.context['total'] == 25
    assert first.context['repositories'][0].name == 'lab-24'
    assert len(first.context['repositories']) == 20
    html = first.content.decode().replace('&amp;', '&')
    link = re.search(r'href="([^\"]+)">Далее', html).group(1)
    parsed = parse_qs(urlsplit(link).query)
    for key, value in params.items():
        assert parsed[key] == [value]
    second = client.get(url + link)
    assert second.status_code == 200
    assert second.context['page_obj'].number == 2
    assert len(second.context['repositories']) == 5
    assert second.context['repositories'][0].name == 'lab-04'
    assert not second.context['page_obj'].has_next()


@pytest.mark.parametrize('params', [
    {'sort': 'name; DROP TABLE'}, {'project_id': '999'},
    {'project_id': '-1'}, {'page': '999'}, {'page': '9' * 100},
])
def test_new_invalid_parameters(web, params):
    response = web[0].get('/repositories/', params)
    assert response.status_code == 400
    assert response.context['error']


def test_related_search_zero_counts_and_aggregates(web):
    client, _ = web
    Repository.objects.create(project_id=11, name='empty',
                              clone_url='https://example.org')
    response = client.get('/repositories/', {'q': 'Тестовый проект'})
    assert response.context['total'] == 2
    stats = client.get('/statistics/', {'min_members': '0'}).context
    assert {r.name: r.active_count for r in
            stats['repository_statistics']} == {'<b>repo</b>': 1, 'empty': 0}
    assert stats['team_distribution'] == {
        'average': 0.5, 'minimum': 0, 'maximum': 1}
    assert len(stats['popular_repositories']) == 1


def test_select_related_avoids_n_plus_one(web):
    from access.views import member_queryset
    with CaptureQueriesContext(connection) as queries:
        for item in member_queryset():
            assert item.user.username
            assert item.repository.project.owner.full_name
    assert len(queries) == 1
