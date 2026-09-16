"""Функции для работы с git-репозиториями."""


def add_repository(
    repositories: dict[int, dict],
    project_id: int,
    name: str,
    clone_url: str,
    private: bool,
) -> None:
    """Добавить репозиторий в словарь repositories.

    Args:
        repositories: словарь репозиториев, ключ — идентификатор.
        project_id: идентификатор учебного проекта.
        name: короткое имя репозитория.
        clone_url: адрес клонирования.
        private: True, если доступ ограничен.
    """
    repo_id = max(repositories.keys(), default=0) + 1
    repositories[repo_id] = {
        'id': repo_id,
        'project_id': project_id,
        'name': name,
        'clone_url': clone_url,
        'private': private,
    }


def find_repository(
    repositories: dict[int, dict],
    query: str,
) -> list[dict]:
    """Найти репозитории по подстроке названия.

    Args:
        repositories: словарь репозиториев.
        query: фрагмент имени репозитория.

    Returns:
        Список репозиториев, в имени которых встречается query.
    """
    query_lower = query.lower()
    found = []
    for repo in repositories.values():
        if query_lower in repo['name'].lower():
            found.append(repo)
    return found


def visibility_text(private_flag: bool) -> str:
    """Возвращает подпись режима доступа к репозиторию."""
    if private_flag:
        return 'Доступ к репозиторию ограничен'
    return 'Репозиторий открыт для просмотра'


def short_url(url: str) -> str:
    """Сокращает адрес клонирования при печати."""
    if len(url) < 18:
        return 'скрыто'
    return url[0:10] + '***' + url[-8:]


def iter_repos_by_visibility(
    repositories: dict[int, dict],
    private: bool,
):
    """Генератор репозиториев с заданным режимом доступа."""
    for repo in repositories.values():
        if repo['private'] is private:
            yield repo


def filter_repos_by_visibility(
    repositories: dict[int, dict],
    private: bool,
) -> list[dict]:
    """Отобрать репозитории по режиму доступа.

    Args:
        repositories: словарь репозиториев.
        private: True — только закрытые, False — только открытые.

    Returns:
        Список репозиториев выбранного режима доступа.
    """
    return list(iter_repos_by_visibility(repositories, private))


def sort_repos(repositories: dict[int, dict]) -> list[dict]:
    """Отсортировать репозитории по имени.

    Returns:
        Список репозиториев в алфавитном порядке.
    """
    return sorted(
        repositories.values(),
        key=lambda item: item['name'].lower(),
    )
