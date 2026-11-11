"""Адаптация связанных SQL-строк к существующим классам ПР3."""
from datetime import date

from models import Member, Project, Repository, User


def project_from_row(row):
    """Восстановить проект и владельца из результата JOIN."""
    owner = User(row['owner_id'], row['owner_username'],
                 row['owner_full_name'], row['owner_email'] or '')
    return Project(row['project_id'], row['title'], owner,
                   date.fromisoformat(row['opened_on']))


def repository_from_row(row):
    """Сохранить методы и интерфейс Repository для шаблонов ПР6."""
    return Repository(row['repo_id'], project_from_row(row),
                      row['repo_name'], row['clone_url'], bool(row['private']))


def member_from_row(row):
    """Восстановить запись доступа вместе с объектными связями."""
    user = User(row['user_id'], row['username'], row['full_name'],
                row['email'] or '')
    member = Member(row['member_id'], repository_from_row(row), user,
                    row['role'])
    member.is_revoked = bool(row['is_revoked'])
    return member
