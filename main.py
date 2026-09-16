"""Точка запуска сервиса управления репозиториями."""

from datetime import date, datetime

from members import (
    add_member,
    can_push,
    get_access_status,
    get_members_stats,
    remove_member,
)
from projects import days_since_create, find_project, sort_projects
from repositories import (
    filter_repos_by_visibility,
    find_repository,
    short_url,
    sort_repos,
    visibility_text,
)
from storage import (
    load_members,
    load_projects,
    load_repositories,
    save_members,
)
from utils import input_int


def _parse_opened_on(value: str) -> date:
    """Преобразовать дату из JSON в объект date."""
    return datetime.strptime(value, '%Y-%m-%d').date()


def show_projects(projects: dict[int, dict]) -> None:
    """Вывести список учебных проектов."""
    print('\nПроекты:')
    if not projects:
        print('Список проектов пуст.')
        return
    for project in sort_projects(projects):
        opened = _parse_opened_on(project['opened_on'])
        age = days_since_create(opened, date.today())
        print(
            f"{project['id']}. {project['title']} | "
            f"владелец: {project['owner']} | {age} дн."
        )


def show_repositories(
    repositories: dict[int, dict],
    projects: dict[int, dict],
) -> None:
    """Вывести список репозиториев."""
    print('\nРепозитории:')
    if not repositories:
        print('Список репозиториев пуст.')
        return
    for repo in sort_repos(repositories):
        project = projects.get(repo['project_id'], {})
        title = project.get('title', 'без проекта')
        print(
            f"{repo['id']}. {repo['name']} | {title} | "
            f"{visibility_text(repo['private'])} | "
            f"{short_url(repo['clone_url'])}"
        )


def show_members(
    members: list[dict],
    repositories: dict[int, dict],
) -> None:
    """Вывести список участников."""
    print('\nУчастники:')
    if not members:
        print('Список участников пуст.')
        return
    for member in members:
        repo = repositories.get(member['repo_id'], {})
        repo_name = repo.get('name', 'неизвестный репозиторий')
        print(
            f"{member['id']}. {member['username']} | "
            f"роль: {member['role']} | {repo_name}"
        )


def show_stats(
    repositories: dict[int, dict],
    members: list[dict],
) -> None:
    """Показать статистику по репозиториям и ролям."""
    private_count = len(filter_repos_by_visibility(repositories, True))
    public_count = len(filter_repos_by_visibility(repositories, False))
    print('\nСтатистика:')
    print(f'Всего репозиториев: {len(repositories)}')
    print(f'Открытых: {public_count}')
    print(f'Закрытых: {private_count}')
    print(f'Всего участников: {len(members)}')
    stats = get_members_stats(members)
    if not stats:
        print('Участников по ролям нет.')
        return
    for role, count in sorted(stats.items()):
        print(f'Роль {role}: {count}')


def show_pr1_card(
    projects: dict[int, dict],
    repositories: dict[int, dict],
    members: list[dict],
) -> None:
    """Показать карточку из сценария ПР1."""
    if not projects or not repositories:
        print('Недостаточно данных для карточки проекта.')
        return
    project = next(iter(projects.values()))
    repo = next(iter(repositories.values()))
    member = members[0] if members else {'role': 'guest'}
    opened = _parse_opened_on(project['opened_on'])
    age_days = days_since_create(opened, date.today())
    print(f"Владелец: {project['owner']}")
    print(f"Проект: {project['title']}")
    print(f"Репозиторий: {repo['name']}")
    print(f"Клонирование: {short_url(repo['clone_url'])}")
    print(visibility_text(repo['private']))
    print(f'Проекту {age_days} дн.')
    print(get_access_status(can_push(member['role'])))


def search_repository(repositories: dict[int, dict]) -> None:
    """Найти репозиторий по фрагменту имени."""
    query = input('Фрагмент имени репозитория: ').strip()
    found = find_repository(repositories, query)
    if not found:
        print('Репозитории не найдены.')
        return
    for repo in found:
        print(f"{repo['id']}. {repo['name']}")


def search_project(projects: dict[int, dict]) -> None:
    """Найти проект по фрагменту названия."""
    query = input('Фрагмент названия проекта: ').strip()
    found = find_project(projects, query)
    if not found:
        print('Проекты не найдены.')
        return
    for project in found:
        print(f"{project['id']}. {project['title']}")


def check_push_right(members: list[dict]) -> None:
    """Проверить право участника на push."""
    member_id = input_int('Идентификатор участника: ')
    selected = None
    for member in members:
        if member['id'] == member_id:
            selected = member
            break
    if selected is None:
        print('Участник не найден.')
        return
    print(get_access_status(can_push(selected['role'])))


def check_visibility(repositories: dict[int, dict]) -> None:
    """Показать режим доступа репозитория."""
    repo_id = input_int('Идентификатор репозитория: ')
    repo = repositories.get(repo_id)
    if repo is None:
        print('Репозиторий не найден.')
        return
    print(visibility_text(repo['private']))


def add_member_interactive(
    members: list[dict],
    repositories: dict[int, dict],
) -> None:
    """Добавить участника и сохранить изменения."""
    repo_id = input_int('Идентификатор репозитория: ')
    if repo_id not in repositories:
        print('Репозиторий не найден.')
        return
    username = input('Имя пользователя: ').strip()
    role = input('Роль (owner/maintainer/developer): ').strip()
    try:
        add_member(members, repo_id, username, role)
    except ValueError as error:
        print(error)
        return
    save_members(members)
    print('Участник добавлен.')


def remove_member_interactive(members: list[dict]) -> None:
    """Удалить участника и сохранить изменения."""
    member_id = input_int('Идентификатор участника: ')
    if remove_member(members, member_id):
        save_members(members)
        print('Участник удалён.')
        return
    print('Участник не найден.')


def print_menu() -> None:
    """Вывести меню приложения."""
    print('\n=== Сервис управления репозиториями ===')
    print('1. Показать репозитории')
    print('2. Найти репозиторий по названию')
    print('3. Проверить право на push')
    print('4. Проверить режим доступа')
    print('5. Добавить участника')
    print('6. Удалить участника')
    print('7. Показать участников')
    print('8. Показать проекты')
    print('9. Найти проект по названию')
    print('10. Статистика')
    print('11. Карточка проекта (сценарий ПР1)')
    print('0. Выход')


def main() -> None:
    """Точка запуска: цикл меню и вызов функций проекта."""
    projects = load_projects()
    repositories = load_repositories()
    members = load_members()
    actions = {
        1: lambda: show_repositories(repositories, projects),
        2: lambda: search_repository(repositories),
        3: lambda: check_push_right(members),
        4: lambda: check_visibility(repositories),
        5: lambda: add_member_interactive(members, repositories),
        6: lambda: remove_member_interactive(members),
        7: lambda: show_members(members, repositories),
        8: lambda: show_projects(projects),
        9: lambda: search_project(projects),
        10: lambda: show_stats(repositories, members),
        11: lambda: show_pr1_card(projects, repositories, members),
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
