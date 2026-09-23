"""Загрузка и сохранение объектов проекта в JSON."""

import json
from pathlib import Path
from typing import Any, cast

from models import Member, Project, Repository, User
from models.projects import get_project_by_id, parse_opened_on
from models.repositories import get_repository_by_id
from models.users import get_user_by_id

DATA_DIR = Path(__file__).resolve().parent / 'data'


def _resolve(filename: str) -> Path:
    """Вернуть абсолютный путь к файлу данных."""
    path = Path(filename)
    if path.is_absolute():
        return path
    return DATA_DIR / filename


def _load_list(filename: str) -> list[dict[str, Any]]:
    """Прочитать JSON-список. При ошибке вернуть пустой список."""
    path = _resolve(filename)
    try:
        with open(path, 'r', encoding='utf-8') as file:
            data = json.load(file)
    except FileNotFoundError:
        return []
    except json.JSONDecodeError:
        return []
    if not isinstance(data, list):
        return []
    return cast(list[dict[str, Any]], data)


def _save_list(filename: str, records: list[dict[str, Any]]) -> None:
    """Записать список словарей в JSON-файл."""
    path = _resolve(filename)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, 'w', encoding='utf-8') as file:
        json.dump(records, file, ensure_ascii=False, indent=2)


def load_users(filename: str = 'users.json') -> list[User]:
    """Загрузить пользователей из JSON как объекты User."""
    return [User.from_data(item) for item in _load_list(filename)]


def save_users(
    users: list[User],
    filename: str = 'users.json',
) -> None:
    """Сохранить объекты User в JSON."""
    _save_list(filename, [user.to_dict() for user in users])


def load_projects(
    users: list[User],
    filename: str = 'projects.json',
) -> list[Project]:
    """Загрузить проекты и связать их с объектами User."""
    projects: list[Project] = []
    for data in _load_list(filename):
        owner = get_user_by_id(users, int(data['owner_id']))
        if owner is None:
            continue
        projects.append(
            Project(
                int(data['id']),
                str(data['title']),
                owner,
                parse_opened_on(str(data['opened_on'])),
            )
        )
    return projects


def save_projects(
    projects: list[Project],
    filename: str = 'projects.json',
) -> None:
    """Сохранить объекты Project в JSON."""
    _save_list(filename, [project.to_dict() for project in projects])


def load_repositories(
    projects: list[Project],
    filename: str = 'repositories.json',
) -> list[Repository]:
    """Загрузить репозитории и связать их с объектами Project."""
    repositories: list[Repository] = []
    for data in _load_list(filename):
        project = get_project_by_id(projects, int(data['project_id']))
        if project is None:
            continue
        repositories.append(
            Repository(
                int(data['id']),
                project,
                str(data['name']),
                str(data['clone_url']),
                bool(data['private']),
            )
        )
    return repositories


def save_repositories(
    repositories: list[Repository],
    filename: str = 'repositories.json',
) -> None:
    """Сохранить объекты Repository в JSON."""
    _save_list(filename, [repo.to_dict() for repo in repositories])


def load_members(
    repositories: list[Repository],
    users: list[User],
    filename: str = 'members.json',
) -> list[Member]:
    """Загрузить участников и восстановить ссылки на объекты."""
    members: list[Member] = []
    for data in _load_list(filename):
        repo = get_repository_by_id(repositories, int(data['repo_id']))
        user = get_user_by_id(users, int(data['user_id']))
        if repo is None or user is None:
            continue
        member = Member(
            int(data['id']),
            repo,
            user,
            str(data['role']),
        )
        member.is_revoked = bool(data.get('is_revoked', False))
        members.append(member)
    return members


def save_members(
    members: list[Member],
    filename: str = 'members.json',
) -> None:
    """Сохранить объекты Member в JSON."""
    _save_list(filename, [member.to_dict() for member in members])
