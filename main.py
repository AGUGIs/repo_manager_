"""Точка запуска сервиса управления репозиториями."""

from datetime import date

from models import Member, Project, Repository, User
from models.members import (
    add_member,
    can_push,
    get_access_status,
    get_member_by_id,
    get_members_stats,
    revoke_member,
    show_members,
)
from models.projects import find_project, show_projects
from models.repositories import (
    filter_repos_by_visibility,
    find_repository,
    get_repository_by_id,
    show_repositories,
)
from models.users import (
    add_user,
    find_user,
    get_user_by_username,
    show_users,
)
from storage import (
    load_members,
    load_projects,
    load_repositories,
    load_users,
    save_members,
    save_users,
)
from utils import input_int


def show_stats(
    repositories: list[Repository],
    members: list[Member],
    users: list[User],
) -> None:
    """Показать статистику по репозиториям, ролям и пользователям."""
    private_count = len(filter_repos_by_visibility(repositories, True))
    public_count = len(filter_repos_by_visibility(repositories, False))
    print('\nСтатистика:')
    print(f'Всего пользователей: {len(users)}')
    print(f'Всего репозиториев: {len(repositories)}')
    print(f'Открытых: {public_count}')
    print(f'Закрытых: {private_count}')
    print(f'Всего участников: {len(members)}')
    stats = get_members_stats(members)
    if not stats:
        print('Активных участников по ролям нет.')
        return
    for role, count in sorted(stats.items()):
        print(f'Роль {role}: {count}')


def show_pr1_card(
    projects: list[Project],
    repositories: list[Repository],
    members: list[Member],
) -> None:
    """Показать карточку из сценария ПР1."""
    if not projects or not repositories:
        print('Недостаточно данных для карточки проекта.')
        return
    project = projects[0]
    repo = repositories[0]
    member = members[0] if members else None
    print(f'Владелец: {project.owner}')
    print(f'Проект: {project.title}')
    print(f'Репозиторий: {repo.name}')
    print(f'Клонирование: {repo.masked_url()}')
    print(repo.visibility_text())
    print(f'Проекту {project.days_since(date.today())} дн.')
    if member is None:
        print(get_access_status(can_push('guest')))
        return
    print(member.access_status())


def print_separator() -> None:
    """Напечатать разделительную полосу перед результатом."""
    print('=========================================')


def search_repository(repositories: list[Repository]) -> None:
    """Найти репозиторий по фрагменту имени."""
    query = input('Фрагмент имени репозитория: ').strip()
    print_separator()
    found = find_repository(repositories, query)
    if not found:
        print('Репозитории не найдены.')
        return
    for repo in found:
        print(f'{repo.id}. {repo.name}')


def search_project(projects: list[Project]) -> None:
    """Найти проект по фрагменту названия."""
    query = input('Фрагмент названия проекта: ').strip()
    print_separator()
    found = find_project(projects, query)
    if not found:
        print('Проекты не найдены.')
        return
    for project in found:
        print(f'{project.id}. {project.title}')


def search_user(users: list[User]) -> None:
    """Найти пользователя по логину или ФИО."""
    query = input('Фрагмент логина или ФИО: ').strip()
    print_separator()
    found = find_user(users, query)
    if not found:
        print('Пользователи не найдены.')
        return
    for user in found:
        print(f'{user.id}. {user}')


def check_push_right(members: list[Member]) -> None:
    """Проверить право участника на push."""
    member_id = input_int('Идентификатор участника: ')
    selected = get_member_by_id(members, member_id)
    if selected is None:
        print('Участник не найден.')
        return
    print(selected.access_status())


def check_visibility(repositories: list[Repository]) -> None:
    """Показать режим доступа репозитория."""
    repo_id = input_int('Идентификатор репозитория: ')
    repo = get_repository_by_id(repositories, repo_id)
    if repo is None:
        print('Репозиторий не найден.')
        return
    print(repo.visibility_text())


def add_user_interactive(users: list[User]) -> None:
    """Добавить пользователя и сохранить изменения."""
    username = input('Логин: ').strip()
    full_name = input('ФИО: ').strip()
    email = input('Email: ').strip()
    try:
        add_user(users, username, full_name, email)
    except ValueError as error:
        print(error)
        return
    save_users(users)
    print('Пользователь добавлен.')


def add_member_interactive(
    members: list[Member],
    repositories: list[Repository],
    users: list[User],
) -> None:
    """Добавить участника и сохранить изменения."""
    repo_id = input_int('Идентификатор репозитория: ')
    repo = get_repository_by_id(repositories, repo_id)
    if repo is None:
        print('Репозиторий не найден.')
        return
    username = input('Логин пользователя: ').strip()
    user = get_user_by_username(users, username)
    if user is None:
        print('Пользователь не найден. Сначала добавьте его.')
        return
    role = input('Роль (owner/maintainer/developer): ').strip()
    try:
        add_member(members, repo, user, role)
    except ValueError as error:
        print(error)
        return
    save_members(members)
    print('Участник добавлен.')


def revoke_member_interactive(members: list[Member]) -> None:
    """Отозвать доступ участника и сохранить изменения."""
    member_id = input_int('Идентификатор участника: ')
    if revoke_member(members, member_id):
        save_members(members)
        print('Доступ участника отозван.')
        return
    print('Активный участник не найден.')


def print_menu() -> None:
    """Вывести меню приложения."""
    print('\n=== Сервис управления репозиториями ===')
    print('1. Показать репозитории')
    print('2. Найти репозиторий по названию')
    print('3. Проверить право на push')
    print('4. Проверить режим доступа')
    print('5. Добавить участника')
    print('6. Отозвать доступ участника')
    print('7. Показать участников')
    print('8. Показать проекты')
    print('9. Найти проект по названию')
    print('10. Статистика')
    print('11. Карточка проекта (сценарий ПР1)')
    print('12. Показать пользователей')
    print('13. Найти пользователя')
    print('14. Добавить пользователя')
    print('0. Выход')
    print('=========================================')


def main() -> None:
    """Точка запуска: цикл меню и коллекции объектов."""
    users = load_users()
    projects = load_projects(users)
    repositories = load_repositories(projects)
    members = load_members(repositories, users)
    actions = {
        1: lambda: show_repositories(repositories),
        2: lambda: search_repository(repositories),
        3: lambda: check_push_right(members),
        4: lambda: check_visibility(repositories),
        5: lambda: add_member_interactive(members, repositories, users),
        6: lambda: revoke_member_interactive(members),
        7: lambda: show_members(members),
        8: lambda: show_projects(projects),
        9: lambda: search_project(projects),
        10: lambda: show_stats(repositories, members, users),
        11: lambda: show_pr1_card(projects, repositories, members),
        12: lambda: show_users(users),
        13: lambda: search_user(users),
        14: lambda: add_user_interactive(users),
    }
    while True:
        print_menu()
        try:
            choice = input_int('Выберите действие: ')
        except (EOFError, KeyboardInterrupt):
            print('\nВыход.')
            break
        if choice == 0:
            print('Выход.')
            break
        action = actions.get(choice)
        if action is None:
            print('Нет такого пункта меню.')
            continue
        action()


if __name__ == '__main__':
    main()
