# Сервис управления репозиториями проектов

Консольное приложение для учёта учебных проектов, git-репозиториев
и прав участников. Практическая работа № 3: объектная модель
предметной области.
Студент: Челышев Кирилл, ЭФБО-10-24.

## Возможности

- просмотр и поиск проектов, репозиториев и пользователей;
- проверка режима доступа к репозиторию;
- проверка права участника на push;
- добавление участников и отзыв доступа;
- добавление пользователей;
- статистика по репозиториям и ролям;
- карточка проекта из сценария ПР1.

## Предметная область

Основные объекты:

- пользователь (`User`);
- учебный проект (`Project`);
- git-репозиторий (`Repository`);
- участник репозитория (`Member`).

`Member` связывает объекты `User` и `Repository`. Один человек может
иметь разные роли в разных репозиториях. Отзыв доступа не удаляет
запись: меняется состояние `is_revoked`.

## Основные классы

### User

Атрибуты: `id`, `username`, `full_name`, `email`.

Методы: `from_data()`, `validate_username()`, `matches()`, `to_dict()`,
`__str__()`.

### Project

Атрибуты: `id`, `title`, `owner` (объект `User`), `opened_on`.

Методы: `days_since()`, `matches()`, `to_dict()`, `__str__()`.

### Repository

Атрибуты: `id`, `project` (объект `Project`), `name`, `clone_url`,
`private`.

Методы: `visibility_text()`, `masked_url()`, `matches()`, `to_dict()`,
`__str__()`.

### Member

Атрибуты: `id`, `repository` (объект `Repository`), `user` (объект
`User`), `role`, `is_revoked`.

Методы: `can_push()`, `revoke()`, `access_status()`, `to_dict()`,
`__str__()`.

Все классы наследуют `DomainEntity`: общий идентификатор и метод
`to_dict()`.

## Структура проекта

```text
repo-manager/
├── main.py
├── storage.py
├── utils.py
├── models/
│   ├── base.py
│   ├── users.py
│   ├── projects.py
│   ├── repositories.py
│   └── members.py
├── data/
│   ├── users.json
│   ├── projects.json
│   ├── repositories.json
│   └── members.json
└── tests/
```

## Хранение данных

JSON хранит идентификаторы связей (`owner_id`, `project_id`,
`repo_id`, `user_id`). При загрузке `storage.py` восстанавливает
ссылки на объекты. При сохранении объекты снова превращаются в
идентификаторы.

## Требования

- Python 3.x;
- pytest;
- flake8;
- autopep8;
- mypy.

```bash
pip install -r requirements.txt
```

## Запуск программы

```bash
python3 main.py
```

## Запуск тестов

```bash
pytest -v
```

## Проверка качества кода

```bash
make check
```

## Сценарий ПР1

Методы `visibility_text()`, `days_since()`, `can_push()` и
`masked_url()` сохраняют поведение функций ПР1. Пункт меню 11
печатает карточку проекта по объектам, загруженным из JSON.
