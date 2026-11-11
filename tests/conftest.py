"""Проверки HTTP, объектов JSON, экранирования и отсутствия записи."""
import os
from datetime import date

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

import django  # noqa: E402

django.setup()

from django.test import Client, override_settings  # noqa: E402
from django.test.utils import (  # noqa: E402
    setup_test_environment, teardown_test_environment,
    setup_databases, teardown_databases,
)
import pytest  # noqa: E402

from models import Member, Project, Repository, User  # noqa: E402
import storage  # noqa: E402
from db import database  # noqa: E402
from db.import_json import import_data  # noqa: E402


@pytest.fixture(scope='session', autouse=True)
def template_instrumentation():
    """Собирать шаблоны и контекст реальных HTTP-ответов."""
    setup_test_environment()
    databases = setup_databases(verbosity=0, interactive=False)
    yield
    teardown_databases(databases, verbosity=0)
    teardown_test_environment()


@pytest.fixture
def web(tmp_path, monkeypatch):
    data = tmp_path / 'json'
    data.mkdir()
    monkeypatch.setattr(storage, 'DATA_DIR', data)
    monkeypatch.setattr(database, 'DB_PATH', tmp_path / 'test.sqlite')
    user = User(7, 'tester', '<script>alert(1)</script>', 'test@example.org')
    project = Project(11, 'Тестовый проект', user, date(2026, 1, 1))
    repo = Repository(13, project, '<b>repo</b>',
                      'https://example.org/test.git', True)
    writer = Member(17, repo, user, 'maintainer')
    revoked = Member(18, repo, user, 'owner')
    revoked.revoke()
    storage.save_users([user])
    storage.save_projects([project])
    storage.save_repositories([repo])
    storage.save_members([writer, revoked])
    import_data(folder=data)
    sync_orm()
    with override_settings(ALLOWED_HOSTS=['testserver'], DEBUG=False):
        yield Client(), data


def sync_orm():
    """Пересоздать тестовую ORM-копию после изменения источника ПР7."""
    from catalog.management.commands.import_pr7 import import_source
    from access.models import Member, User
    from catalog.models import Project, Repository
    Member.objects.all().delete()
    Repository.objects.all().delete()
    Project.objects.all().delete()
    User.objects.all().delete()
    import_source(database.DB_PATH)
