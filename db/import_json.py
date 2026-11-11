"""Явный транзакционный импорт JSON; запуск: python -m db.import_json."""
import argparse
from contextlib import closing
from datetime import date
import json
from pathlib import Path
import sqlite3

from . import database

TABLES = ('users', 'projects', 'repositories', 'members')
COLUMNS = {
    'users': ('id', 'username', 'full_name', 'email'),
    'projects': ('id', 'title', 'owner_id', 'opened_on'),
    'repositories': ('id', 'project_id', 'name', 'clone_url', 'private'),
    'members': ('id', 'repo_id', 'user_id', 'role', 'is_revoked'),
}


def load_records(folder, table):
    """Читать исходные файлы строго: ошибки не превращаются в пустые данные."""
    path = folder / (table + '.json')
    records = json.loads(path.read_text(encoding='utf-8'))
    if not isinstance(records, list):
        raise ValueError(f'{path.name}: ожидался список записей')
    seen = set()
    result = []
    for record in records:
        if not isinstance(record, dict):
            raise ValueError(f'{path.name}: запись должна быть объектом')
        record = dict(record)
        if table == 'users':
            record['email'] = record.get('email') or None
        if table == 'members':
            record.setdefault('is_revoked', False)
        for key in COLUMNS[table]:
            if key not in record:
                raise ValueError(f'{path.name}: отсутствует поле {key}')
            value = record[key]
            if key == 'id' or key.endswith('_id'):
                if type(value) is not int or value <= 0:
                    raise ValueError(f'{path.name}: {key} должен быть > 0')
            elif key in ('private', 'is_revoked'):
                if type(value) not in (bool, int) or value not in (0, 1):
                    raise ValueError(f'{path.name}: {key} должен быть 0 или 1')
            elif value is not None or key != 'email':
                if not isinstance(value, str):
                    raise ValueError(f'{path.name}: {key} должен быть строкой')
        if record['id'] in seen:
            raise ValueError(f'{path.name}: повторный id {record["id"]}')
        seen.add(record['id'])
        if table == 'projects':
            date.fromisoformat(record['opened_on'])
        result.append(tuple(record[key] for key in COLUMNS[table]))
    return result


def import_data(folder=None, path=None, *, replace=False):
    """Импортировать в порядке связей; при ошибке откатить все записи.

    Повторный импорт обновляет записи по id, не создавая дубликатов.
    Только явный replace удаляет записи, отсутствующие в исходном JSON.
    """
    folder = Path(folder) if folder is not None else database.BASE_DIR / 'data'
    records = {table: load_records(folder, table) for table in TABLES}
    database.initialize(path)
    with closing(database.get_connection(path)) as connection:
        with connection:
            if replace:
                for table in reversed(TABLES):
                    connection.execute('DELETE FROM ' + table)
            for table in TABLES:
                columns = COLUMNS[table]
                # Имена таблиц и столбцов взяты только из констант выше.
                fields = ', '.join(columns)
                placeholders = ', '.join('?' for _ in columns)
                updates = ', '.join(
                    f'{key}=excluded.{key}' for key in columns if key != 'id'
                )
                sql = (f'INSERT INTO {table} ({fields}) '
                       f'VALUES ({placeholders}) '
                       f'ON CONFLICT(id) DO UPDATE SET {updates}')
                connection.executemany(sql, records[table])
    return {table: len(records[table]) for table in TABLES}


def main():
    """Импортировать данные по явной команде разработчика."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--replace', action='store_true',
                        help='заменить содержимое базы снимком из JSON')
    args = parser.parse_args()
    try:
        counts = import_data(replace=args.replace)
    except (OSError, ValueError, sqlite3.Error) as error:
        parser.exit(1, f'Импорт не выполнен: {error}\n')
    print('Импорт завершён: ' + ', '.join(
        f'{table}: {count}' for table, count in counts.items()))


if __name__ == '__main__':
    main()
