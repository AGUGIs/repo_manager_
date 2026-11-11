"""Однократный перенос из SQLite ПР7 в отдельную базу Django."""
from contextlib import closing
from datetime import date
from pathlib import Path
import sqlite3

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db import IntegrityError, transaction

from access.models import Member, User
from catalog.models import Project, Repository

# Имена таблиц и полей фиксированы; пользователь задаёт только путь к файлу.
SPECS = [
    ('users', User, ['id', 'username', 'full_name', 'email']),
    ('projects', Project, ['id', 'title', 'owner_id', 'opened_on']),
    ('repositories', Repository,
     ['id', 'project_id', 'name', 'clone_url', 'private']),
    ('members', Member,
     ['id', 'repository_id', 'user_id', 'role', 'is_revoked']),
]


def import_source(source):
    """Атомарный импорт с проверкой повторного запуска без перезаписи."""
    source = Path(source).resolve()
    target = Path(settings.DATABASES['default']['NAME']).resolve()
    if source == target:
        raise ValueError('Источник и база Django должны различаться.')
    snapshots = []
    uri = source.as_uri() + '?mode=ro'
    with closing(sqlite3.connect(uri, uri=True)) as db:
        db.row_factory = sqlite3.Row
        db.execute('BEGIN')
        for table, model, fields in SPECS:
            columns = ['repo_id' if f ==
                       'repository_id' else f for f in fields]
            rows = db.execute(
                f'SELECT {", ".join(columns)} FROM {table} ORDER BY id')
            records = []
            for row in rows:
                record = dict(zip(fields, row))
                for field in ('private', 'is_revoked'):
                    if field in record:
                        if record[field] not in (0, 1):
                            raise ValueError(f'{table}: неверный {field}')
                        record[field] = bool(record[field])
                if 'opened_on' in record:
                    record['opened_on'] = date.fromisoformat(
                        record['opened_on'])
                records.append(record)
            snapshots.append((model, fields, records))
    with transaction.atomic():
        if any(model.objects.exists() for _, model, _ in SPECS):
            for model, fields, records in snapshots:
                current = list(model.objects.order_by('id').values(*fields))
                if current != records:
                    raise ValueError(
                        'База Django уже содержит отличающиеся данные. '
                        'Импорт остановлен без изменений.')
        else:
            for model, fields, records in snapshots:
                model.objects.bulk_create([model(**row) for row in records])
    return {model.__name__: len(records)
            for model, _, records in snapshots}


class Command(BaseCommand):
    help = 'Перенос ПР7: чтение источника без изменения исходного файла'

    def add_arguments(self, parser):
        parser.add_argument('--source', type=Path,
                            default=settings.BASE_DIR / 'data' /
                            'repo_manager.sqlite')

    def handle(self, *args, **options):
        try:
            counts = import_source(options['source'])
        except (ValueError, sqlite3.Error, IntegrityError) as exc:
            raise CommandError(str(exc)) from exc
        self.stdout.write(self.style.SUCCESS(f'Перенос проверен: {counts}'))
