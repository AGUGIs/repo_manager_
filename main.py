from datetime import date


def visibility_text(private_flag: bool) -> str:
    """Возвращает подпись режима доступа к репозиторию."""
    if private_flag:
        return 'Доступ к репозиторию ограничен'
    return 'Репозиторий открыт для просмотра'


def days_since_create(start: date, current: date) -> int:
    """Считает, сколько дней прошло с создания проекта."""
    delta = current - start
    return delta.days


def can_push(role: str) -> bool:
    """Проверяет, может ли участник отправлять изменения."""
    if role == 'owner':
        return True
    if role == 'maintainer':
        return True
    return False


def short_url(url: str) -> str:
    """Сокращает адрес клонирования при печати."""
    if len(url) < 18:
        return 'скрыто'
    return url[0:10] + '***' + url[-8:]


owner_name = 'Кирилл Челышев'
project_title = 'Курсовой дневник'
repository = 'course-notes'
git_url = 'https://gitlab.local/course-notes.git'
private_flag = False
role = 'maintainer'
opened_on = date(2026, 2, 3)
current_day = date(2026, 9, 10)
age_days = days_since_create(opened_on, current_day)

print(f'Владелец: {owner_name}')
print(f'Проект: {project_title}')
print(f'Репозиторий: {repository}')
print(f'Клонирование: {short_url(git_url)}')
print(visibility_text(private_flag))
print(f'Проекту {age_days} дн.')

if can_push(role):
    print('Участник может выполнять push.')
else:
    print('Push для этой роли запрещён.')
