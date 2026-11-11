"""HTTP-проверки интерфейса ПР5–ПР7 на временной SQLite-базе."""
from django.test import override_settings
import pytest

from db.import_json import import_data
import storage
from conftest import sync_orm


@pytest.mark.parametrize('url', [
    '/', '/projects/', '/projects/11/', '/repositories/',
    '/repositories/13/', '/members/', '/members/17/', '/members/18/',
])
def test_pages_and_read_only(web, url):
    client, data = web
    before = {p.name: p.read_bytes() for p in data.iterdir()}
    response = client.get(url)
    assert response.status_code == 200
    assert response['Content-Type'] == 'text/html; charset=utf-8'
    assert b'<script>alert(1)</script>' not in response.content
    assert b'<b>repo</b>' not in response.content
    assert b'<nav' in response.content
    assert before == {p.name: p.read_bytes() for p in data.iterdir()}


@pytest.mark.parametrize('url', [
    '/missing/', '/projects/999/', '/repositories/999/',
    '/members/999/', '/repositories/abc/',
])
def test_custom_404(web, url):
    response = web[0].get(url)
    assert response.status_code == 404
    assert 'Страница не найдена' in response.content.decode()
    assert 'На главную' in response.content.decode()


def test_permissions_and_relationships(web):
    client, _ = web
    assert 'Участник может выполнять push.' in (
        client.get('/members/17/').content.decode())
    revoked = client.get('/members/18/').content.decode()
    assert 'Доступ отозван' in revoked
    assert 'Push для этой роли запрещён.' in revoked
    repo = client.get('/repositories/13/').content.decode()
    assert 'href="/projects/11/"' in repo
    assert '&lt;b&gt;repo&lt;/b&gt;' in repo
    assert 'Доступ к репозиторию ограничен' in repo


def test_empty_data_and_unsupported_method(web):
    client, data = web
    for path in data.iterdir():
        path.write_text('[]')
    import_data(folder=data, replace=True)
    sync_orm()
    for url, text in [('/projects/', 'Проектов пока нет.'),
                      ('/repositories/', 'Репозиториев пока нет.'),
                      ('/members/', 'Участников пока нет.')]:
        assert text in client.get(url).content.decode()
    assert client.post('/members/').status_code == 405


@pytest.mark.parametrize('url,template,key', [
    ('/', 'homepage/index.html', None),
    ('/projects/', 'catalog/project_list.html', 'projects'),
    ('/projects/11/', 'catalog/project_detail.html', 'project'),
    ('/repositories/', 'catalog/repository_list.html', 'repositories'),
    ('/repositories/13/', 'catalog/repository_detail.html', 'repository'),
    ('/members/', 'access/member_list.html', 'members'),
    ('/members/17/', 'access/member_detail.html', 'member'),
    ('/missing/', '404.html', None),
])
def test_templates_and_context(web, url, template, key):
    response = web[0].get(url)
    used = {item.name for item in response.templates}
    assert {template, 'base.html', 'includes/navigation.html'} <= used
    if key is not None:
        assert response.context[key]
    html = response.content.decode()
    for asset in ['css/style.css', 'js/main.js', 'img/logo.svg']:
        assert '/static/homepage/' + asset in html


def test_template_filters(web):
    client, _ = web
    users = storage.load_users()
    projects = storage.load_projects(users)
    projects[0].title = ''
    storage.save_projects(projects)
    import_data(folder=storage.DATA_DIR, replace=True)
    sync_orm()
    html = client.get('/projects/').content.decode()
    assert 'Без названия' in html
    assert '01.01.2026' in html
    assert 'Всего проектов: 1' in html
    assert 'Всего репозиториев: 1' in (
        client.get('/projects/11/').content.decode())


def test_public_visibility(web):
    client, data = web
    import json
    path = data / 'repositories.json'
    records = json.loads(path.read_text())
    records[0]['private'] = False
    path.write_text(json.dumps(records))
    import_data(folder=data, replace=True)
    sync_orm()
    for url in ['/repositories/', '/repositories/13/']:
        html = client.get(url).content.decode()
        assert 'Репозиторий открыт для просмотра' in html
        assert 'repo-status-public' in html
        assert 'Доступ к репозиторию ограничен' not in html


@pytest.mark.parametrize('asset', [
    'homepage/css/style.css', 'homepage/js/main.js', 'homepage/img/logo.svg',
])
def test_static_discovery_and_configurable_url(web, asset):
    from django.contrib.staticfiles import finders
    from pathlib import Path
    assert Path(finders.find(asset)).is_file()
    with override_settings(STATIC_URL='/assets/'):
        html = web[0].get('/').content.decode()
        assert '/assets/' + asset in html


def test_active_navigation(web):
    html = web[0].get('/repositories/13/').content.decode()
    assert 'href="/repositories/" aria-current="page"' in html
    assert html.count('aria-current="page"') == 1
    assert 'href="/members/"' in html


def test_empty_related_lists(web):
    client, _ = web
    storage.save_members([])
    import_data(folder=storage.DATA_DIR, replace=True)
    sync_orm()
    assert 'Участников пока нет.' in (
        client.get('/repositories/13/').content.decode())
    storage.save_repositories([])
    import_data(folder=storage.DATA_DIR, replace=True)
    sync_orm()
    assert 'Репозиториев пока нет.' in (
        client.get('/projects/11/').content.decode())
