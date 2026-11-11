"""Загрузка связанного графа объектов ПР3 для одного запроса."""
from storage import (load_members, load_projects, load_repositories,
                     load_users)


def load_domain():
    """Сохранить порядок восстановления объектных связей из JSON."""
    users = load_users()
    projects = load_projects(users)
    repositories = load_repositories(projects)
    members = load_members(repositories, users)
    return users, projects, repositories, members
