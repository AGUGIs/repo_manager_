"""SQL, импорт, целостность, фильтрация и веб-сценарии ПР7."""
from contextlib import closing
import json
import sqlite3

import pytest

from conftest import sync_orm

from db import database
from db.import_json import import_data


def test_import_repeat_and_foreign_keys(web):
    _, folder = web
    initial = dict(database.fetch_one('counts'))
    import_data(folder)
    import_data(folder)
    assert dict(database.fetch_one('counts')) == initial
    database.initialize()
    assert dict(database.fetch_one('counts')) == initial
    with closing(database.get_connection()) as conn:
        assert conn.execute('PRAGMA foreign_keys').fetchone()[0] == 1
        assert conn.execute('PRAGMA foreign_key_check').fetchall() == []
        assert conn.execute('PRAGMA integrity_check').fetchone()[0] == 'ok'


@pytest.mark.parametrize('sql', [
    "INSERT INTO users VALUES (9, 'tester', 'Duplicate', NULL)",
    "INSERT INTO users VALUES (9, '', 'Empty', NULL)",
    "INSERT INTO members VALUES (19, 999, 7, 'owner', 0)",
    "INSERT INTO members VALUES (19, 13, 999, 'owner', 0)",
    "INSERT INTO members VALUES (19, 13, 7, 'owner', 0)",
    "INSERT INTO members VALUES (19, 13, 7, 'owner', 2)",
    "UPDATE repositories SET private=2 WHERE id=13",
    "DELETE FROM users WHERE id=7",
])
def test_database_constraints(web, sql):
    with closing(database.get_connection()) as conn:
        with pytest.raises(sqlite3.IntegrityError):
            with conn:
                conn.execute(sql)


def test_failed_import_rolls_back_all_tables(web):
    _, folder = web
    users = json.loads((folder / 'users.json').read_text())
    users[0]['full_name'] = 'Should roll back'
    (folder / 'users.json').write_text(json.dumps(users))
    members = json.loads((folder / 'members.json').read_text())
    members[0]['repo_id'] = 999
    (folder / 'members.json').write_text(json.dumps(members))
    before = [dict(row) for row in database.fetch_all('users')]
    with pytest.raises(sqlite3.IntegrityError):
        import_data(folder, replace=True)
    assert [dict(row) for row in database.fetch_all('users')] == before
    assert database.fetch_one('counts')['members'] == 2


def test_invalid_json_does_not_erase_database(web):
    _, folder = web
    (folder / 'users.json').write_text('{broken')
    with pytest.raises(ValueError):
        import_data(folder, replace=True)
    assert database.fetch_one('counts')['users'] == 1


@pytest.mark.parametrize('name,params', [
    ('users', {}), ('projects', {}), ('project_detail', {'id': 11}),
    ('repositories', {'limit': 20, 'offset': 0}),
    ('repository_detail', {'id': 13}), ('project_repositories', {'id': 11}),
    ('members', {}), ('member_detail', {'id': 17}),
    ('repository_members', {'id': 13}), ('active_members', {}),
    ('search_repositories', {'query': '%', 'private': None, 'user_id': None}),
    ('repository_summary', {}), ('member_summary', {}),
    ('repository_statistics', {}), ('role_statistics', {}),
    ('popular_repositories', {'min_members': 0}),
    ('project_statistics', {}), ('counts', {}),
])
def test_queries_from_sql_file(web, name, params):
    rows = database.fetch_all(name, params)
    assert rows
    assert isinstance(rows[0], sqlite3.Row)
    assert rows[0].keys()


def test_web_reads_sqlite_without_json(web):
    client, folder = web
    for path in folder.iterdir():
        path.unlink()
    for url in ['/projects/', '/projects/11/', '/repositories/',
                '/repositories/13/', '/members/', '/members/17/',
                '/members/active/', '/members/users/', '/statistics/']:
        assert client.get(url).status_code == 200
    assert 'Тестовый проект' in client.get('/projects/').content.decode()


def test_read_only_sql_and_connection_path(web, tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    assert database.fetch_one('counts')['repositories'] == 1
    with closing(database.get_connection(readonly=True)) as conn:
        with pytest.raises(sqlite3.OperationalError):
            conn.execute('DELETE FROM members')
    absent = tmp_path / 'absent.sqlite'
    with pytest.raises(sqlite3.OperationalError):
        database.get_connection(absent, readonly=True)
    assert not absent.exists()


def test_null_email_is_displayed(web):
    client, _ = web
    with closing(database.get_connection()) as conn:
        with conn:
            conn.execute('UPDATE users SET email=NULL WHERE id=7')
    sync_orm()
    response = client.get('/members/users/')
    assert 'Не указана' in response.content.decode()
    assert response.context['users'][0]['email'] is None


def test_active_access_and_search_for_revoked_user(web):
    client, _ = web
    with closing(database.get_connection()) as conn:
        with conn:
            conn.execute('UPDATE members SET is_revoked=1 WHERE id=17')
    sync_orm()
    response = client.get('/members/active/')
    assert response.context['members'] == []
    assert 'Участников пока нет.' in response.content.decode()
    sync_orm()
    response = client.get('/repositories/search/', {'user_id': '7'})
    assert [item.id for item in response.context['repositories']] == [13]


def test_search_initial_results_and_literal_pattern(web):
    client, _ = web
    initial = client.get('/repositories/search/')
    assert not initial.context['searched']
    found = client.get('/repositories/search/', {'q': 'repo'})
    assert [item.id for item in found.context['repositories']] == [13]
    for params in [
        {'q': "' OR 1=1 --"}, {'q': '%'}, {'q': '_'},
        {'q': '\\'}, {'visibility': 'public'}, {'user_id': '7'},
    ]:
        response = client.get('/repositories/search/', params)
        assert response.status_code == 200
        assert response.context['repositories'] == []
        assert 'репозитории не найдены' in response.content.decode()
    assert database.fetch_one('counts')['repositories'] == 1


@pytest.mark.parametrize('url,params', [
    ('/repositories/search/', {'visibility': 'invalid'}),
    ('/repositories/search/', {'user_id': '999'}),
    ('/repositories/search/', {'user_id': '-1'}),
    ('/repositories/search/', {'q': 'x' * 201}),
    ('/statistics/', {'min_members': '-1'}),
    ('/statistics/', {'min_members': '1 OR 1=1'}),
    ('/statistics/', {'min_members': '9' * 100}),
    ('/repositories/', {'page': '0'}),
    ('/repositories/', {'page': 'abc'}),
])
def test_invalid_parameters_return_400(web, url, params):
    response = web[0].get(url, params)
    assert response.status_code == 400
    assert response.context['error']


def test_grouping_zero_counts_having_and_pagination(web):
    client, _ = web
    with closing(database.get_connection()) as conn:
        with conn:
            conn.execute("INSERT INTO repositories VALUES "
                         "(14, 11, 'zero-repo', 'https://example.org/0', 0)")
    rows = database.fetch_all('repository_statistics')
    assert {row['id']: row['active_count'] for row in rows} == {13: 1, 14: 0}
    summary = database.fetch_one('repository_summary')
    assert (summary['total'], summary['public_count'],
            summary['private_count']) == (2, 1, 1)
    members = database.fetch_one('member_summary')
    assert (members['active_count'], members['revoked_count']) == (1, 1)
    assert [row['id'] for row in database.fetch_all(
        'popular_repositories', {'min_members': 0})] == [13]
    assert database.fetch_all('popular_repositories', {'min_members': 1}) == []
    first = database.fetch_all('repositories', {'limit': 1, 'offset': 0})
    second = database.fetch_all('repositories', {'limit': 1, 'offset': 1})
    assert first[0]['repo_id'] != second[0]['repo_id']
    sync_orm()
    response = client.get('/statistics/', {'min_members': '0'})
    assert response.status_code == 200
    assert len(response.context['popular_repositories']) == 1
    assert 'zero-repo' in response.content.decode()


def test_empty_database_statistics(web):
    client, folder = web
    for path in folder.iterdir():
        path.write_text('[]')
    import_data(folder, replace=True)
    sync_orm()
    response = client.get('/statistics/')
    assert response.status_code == 200
    assert response.context['repository_summary']['total'] == 0
    assert response.context['member_summary']['active_count'] == 0
    assert response.context['role_statistics'] == []
