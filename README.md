# Сервис управления репозиториями проектов

Приложение для учёта учебных проектов, Git-репозиториев
и прав участников. ПР3: объектная модель и консольное меню.
ПР5: веб-интерфейс на Django 5.2 с сохранением JSON-хранилища.
ПР6: шаблоны, контекст и статические ресурсы.
ПР7: SQLite, прямой SQL, поиск и статистика.
ПР9: модели Django ORM, миграции, перенос и новые фильтры.
Студент: Челышев Кирилл, ЭФБО-10-24.

## ПР9 — текущая версия и быстрый запуск

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python manage.py migrate
python manage.py import_pr7
python manage.py runserver
```

Откройте http://127.0.0.1:8000/. Веб-страницы используют **db.sqlite3**,
отдельную от исходной **data/repo_manager.sqlite**. Исходник ПР7 сохранён,
его резервная копия — `data/repo_manager_pr7_backup.sqlite`. Если базы ПР7
ещё нет, сначала выполните `python -m db.import_json` из сохранённых JSON.
Не направляйте миграции на старую базу и не применяйте `--fake`.

### Модели и связи

- `access.User`: id (BigAutoField), username (CharField, unique), full_name
  (CharField), email (EmailField, NULL/blank).
- `catalog.Project`: id, title (CharField), opened_on (DateField), owner
  (ForeignKey User, PROTECT, обратная связь `projects`).
- `catalog.Repository`: id, name (CharField), clone_url (URLField), private
  (BooleanField), project (ForeignKey Project, PROTECT, `repositories`).
- `access.Member`: id, role (CharField), is_revoked (BooleanField), repository
  (ForeignKey Repository, CASCADE, `members`), user (ForeignKey User,
  PROTECT, `memberships`). Это связь пользователя и репозитория с ролью
  и историей отзывов. Только один активный доступ на пару repository/user:
  условный UniqueConstraint. Исторические отозванные записи допустимы.

Миграции: `access/0001_initial`, `catalog/0001_initial`, `access/0002_initial`.
Последняя завершает связи между приложениями. `PROTECT` запрещает удалять
владельца проекта, участника с историей доступа и проект с репозиториями;
удаление репозитория каскадно удаляет его записи Member. Метод `revoke()`
сохраняет отзыв, правило push для owner/maintainer сохранено.

### Перенос данных

```bash
python manage.py import_pr7 --source data/repo_manager.sqlite
```

Команда читает источник в режиме read-only и переносит записи через ORM
в одной транзакции в порядке User → Project → Repository → Member,
сохраняя id, связи, даты, NULL и признаки. Повторный запуск сверяет снимки:
при совпадении ничего не меняет, при расхождении останавливается, чтобы
не затереть изменения в новой базе. Ошибка связи откатывает весь перенос.
Автоматической синхронизации консольного JSON и веб-базы нет.

### Страницы и ORM

Все прежние URL и шаблоны сохранены. В `catalog/views.py`,
`catalog/querying.py` и `access/views.py` используются только QuerySet:
`filter`, `exclude`, `get_object_or_404`, `select_related`, обратные связи,
`values`, `annotate`, `aggregate`, Count/Sum/Avg/Min/Max.
SQL-файлы и `db/` сохранены для воспроизведения ПР7 и чтения источника;
веб-представления к ним за данными не обращаются. `db.parameters` содержит
только проверку числового ввода, без доступа к БД.

`/repositories/` и `/repositories/search/` поддерживают параметры:

| Параметр | Значение |
| --- | --- |
| q | Подстрока названия репозитория **или проекта**, максимум 200 символов |
| visibility | all, public, private |
| project_id | Существующий положительный id проекта |
| user_id | Исключить репозитории с активным доступом этого пользователя |
| sort | name, -name, project, newest; по умолчанию name |
| page | Номер страницы от 1; 20 записей на странице |

Пример: `/repositories/?visibility=private&project_id=1&sort=-name&page=1`.
Порядок обработки: валидация → фильтры → сортировка → Paginator.
Сортировки ограничены разрешённым списком, добавлен id для стабильности.
Навигация `{% querystring %}` сохраняет фильтры и сортировку; новая отправка
формы начинает с первой страницы. Некорректные фильтры, номера и страницы
за пределами списка дают 400 с пояснением; отсутствующие карточки — 404.
Пустой список на странице 1 допустим. Отозванный доступ не мешает поиску
репозиториев без активного доступа. Для кириллицы регистронезависимость
`icontains` ограничена возможностями стандартной SQLite.

`/statistics/` сохраняет нулевые команды и проекты без репозиториев,
показывает распределение ролей и средний/минимальный/максимальный размер
команды. Параметр `min_members` фильтрует результат `annotate` по порогу.

### CRUD и выгрузка для защиты

CRUD доступен через Django shell; формы записи в веб-интерфейсе не добавлены.
Пример на отдельных учебных данных:

```python
from datetime import date
from access.models import User, Member
from catalog.models import Project, Repository
u = User.objects.create(username='orm_demo', full_name='Демонстрация')
p = Project.objects.create(title='ORM demo', owner=u, opened_on=date.today())
r = p.repositories.create(name='demo', clone_url='https://example.org/demo')
m = r.members.create(user=u, role='maintainer')
Member.objects.select_related('user', 'repository').get(pk=m.pk)
m.revoke()                           # UPDATE с сохранением истории
Repository.objects.filter(pk=r.pk).update(name='renamed')
r.refresh_from_db()
r.delete()                           # каскадно удалит только его Member
p.delete()
u.delete()
```

```bash
python manage.py dumpdata access catalog --indent 2 -o data/orm_export.json
# loaddata используйте в отдельной пустой базе после migrate
python manage.py loaddata data/orm_export.json
python manage.py check
python manage.py showmigrations
python manage.py makemigrations --check --dry-run
pytest -v
flake8 . --extend-exclude=venv
```

Проверено: 114 тестов. Помимо предыдущих сценариев проверены ORM CRUD,
защита удаления, уникальность активного доступа, откат и повторный перенос,
неизменность источника, независимость веб-базы от JSON/SQL-базы ПР7,
поиск по связанному полю, совместные фильтры/сортировка/пагинация,
сохранение GET-параметров и отсутствие N+1 при чтении Member.
Тесты используют отдельную базу Django и временный источник ПР7.

Ниже сохранена документация предыдущих практических работ.

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

## Веб-интерфейс после ПР7

Текущая версия веб-интерфейса — ПР9, Django ORM. Команды ниже в разделе
ПР7 описывают исторический SQL-слой; актуальный запуск приведён в начале
README в разделе «ПР9». Консольное меню ПР3 по-прежнему использует JSON.

### Установка и запуск

Нужны Python 3.11+ и Django 5.2 (проверено на Python 3.12).
SQLite доступна через стандартную библиотеку, отдельный сервер не нужен.
В проект уже включена база `data/repo_manager.sqlite` с импортированными данными.

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python manage.py check
python manage.py runserver
```

На Windows: `.venv\Scripts\activate`.
Откройте http://127.0.0.1:8000/. Миграции не нужны.
Консольная версия: `python main.py`.

Для создания базы с нуля и импорта исходных файлов:

```bash
python -m db.database
python -m db.import_json
```

Схема использует `CREATE TABLE IF NOT EXISTS`: повторное выполнение сохраняет
данные. Импорт читает JSON, проверяет поля, положительные идентификаторы,
даты, логические значения и дубликаты id; выполняет `executemany()`
в порядке users → projects → repositories → members. Все изменения записей
выполняются в одной транзакции. Ошибка в любой таблице откатывает весь импорт;
исходные JSON не изменяются. Отсутствующий или некорректный файл даёт явную
ошибку вместо импорта пустой коллекции.

Повторный импорт обновляет записи по id через `ON CONFLICT(id) DO UPDATE`,
не добавляя дубликаты. Записи SQLite, которых нет в JSON, при этом сохраняются.
Если нужно явно заменить содержимое базы точным снимком JSON:

```bash
python -m db.import_json --replace
```

Эта команда удаляет прежние записи внутри транзакции в обратном порядке связей,
затем вставляет снимок. Она нужна только для намеренного повторного импорта.
После изменений в консольном меню импорт запускается вручную.

### Структура SQLite

| Таблица | Основные поля | Связи |
| --- | --- | --- |
| `users` | `id INTEGER PRIMARY KEY`, `username TEXT UNIQUE`, `full_name TEXT`, `email TEXT NULL` | Владелец проектов и пользователь доступа |
| `projects` | `id INTEGER PRIMARY KEY`, `title TEXT`, `opened_on TEXT` | `owner_id → users.id` |
| `repositories` | `id INTEGER PRIMARY KEY`, `name TEXT`, `clone_url TEXT`, `private INTEGER` | `project_id → projects.id` |
| `members` | `id INTEGER PRIMARY KEY`, `role TEXT`, `is_revoked INTEGER` | `repo_id → repositories.id`, `user_id → users.id` |

Даты хранятся как ISO-строки YYYY-MM-DD, логические признаки — 0 и 1
с ограничениями CHECK. Обязательные поля имеют NOT NULL.
Проверка внешних ключей включается через `PRAGMA foreign_keys=ON` на каждом
соединении. Частичный UNIQUE-индекс запрещает два активных доступа одного
пользователя к одному репозиторию, сохраняя историю отозванных записей.
Пустая почта импортируется как NULL, в шаблоне показывается «Не указана».
Исходный импорт: 3 пользователя, 2 проекта, 2 репозитория, 3 доступа.

### Файлы слоя базы данных

```text
sql/schema.sql          # таблицы, ограничения и индексы
sql/queries.sql         # 18 именованных SELECT-запросов
db/database.py         # подключения, схема, чтение запросов и результатов
db/import_json.py      # явный транзакционный импорт
db/entities.py         # SQL-строки → классы ПР3 для прежних шаблонов
db/parameters.py       # проверка целочисленных GET-параметров
data/repo_manager.sqlite
```

`DB_PATH` вычисляется от расположения проекта и не зависит от текущего
рабочего каталога. `get_connection()` задаёт `row_factory=sqlite3.Row`,
позволяя читать значения по имени (`row['full_name']`). Все соединения
закрываются через `closing()`. Веб-запросы открывают базу в `mode=ro`:
чтение сайта не меняет данные и не создаёт пустую базу при неверном пути.
Схема и импорт выполняются только явными командами разработчика.

### SQL-запросы и их применение

Файл `sql/queries.sql` — источник запросов, а не отдельная копия примеров.
Каждый запрос имеет метку `-- name: ...`; `fetch_all`/`fetch_one` загружают
его из файла. Параметры передаются отдельным словарём, значения из GET
не вставляются в SQL-строки. Имена запросов задаются кодом приложения.

| Запрос | Назначение и применение |
| --- | --- |
| `users` | Список пользователей, форма поиска |
| `projects` | Проекты с владельцами через JOIN |
| `project_detail` | Проект по id через WHERE |
| `repositories` | Связанные репозитории с ORDER BY, LIMIT и OFFSET |
| `repository_detail` | Репозиторий и его проект с владельцем |
| `project_repositories` | Репозитории выбранного проекта |
| `members` | Все записи доступа через JOIN четырёх сущностей |
| `member_detail` | Связанная информация об участнике |
| `repository_members` | Участники конкретного репозитория |
| `active_members` | Только `is_revoked=0` |
| `search_repositories` | LIKE, фильтр видимости и NOT EXISTS активного доступа |
| `repository_summary` | COUNT, SUM: открытые и закрытые репозитории |
| `member_summary` | COUNT, SUM: активные и отозванные доступы |
| `repository_statistics` | LEFT JOIN и GROUP BY, включая ноль участников |
| `role_statistics` | GROUP BY: количество активных доступов по ролям |
| `popular_repositories` | GROUP BY и HAVING COUNT(...) > заданного порога |
| `project_statistics` | LEFT JOIN и GROUP BY: репозитории по проектам |
| `counts` | Контроль количества записей в четырёх таблицах |

Таким образом, есть более 10 запросов, не менее двух списков, фильтраций WHERE,
JOIN, агрегатных запросов и группировок GROUP BY. Результаты всех запросов
используются веб-страницами. Проверить запрос из Python:

```python
from db.database import fetch_all, fetch_one

print(dict(fetch_one('counts')))
for row in fetch_all('popular_repositories', {'min_members': 1}):
    print(row['name'], row['active_count'])
```

### Страницы и сценарии

| URL | Имя маршрута | Назначение |
| --- | --- | --- |
| `/` | `homepage:index` | Назначение и разделы проекта |
| `/projects/` | `catalog:projects` | Проекты из SQLite |
| `/projects/<int:project_id>/` | `catalog:project_detail` | Проект, владелец, дата и его репозитории |
| `/repositories/` | `catalog:repositories` | Все репозитории, по 20 на страницу |
| `/repositories/<int:repo_id>/` | `catalog:repository_detail` | Репозиторий, проект, режим, участники |
| `/repositories/search/` | `catalog:search` | Поиск по названию, видимости и доступу пользователя |
| `/members/` | `access:members` | Все записи доступа, включая отозванные |
| `/members/active/` | `access:active_members` | Активные доступы, отобранные SQL |
| `/members/users/` | `access:users` | Пользователи, включая не добавленных в репозитории |
| `/members/<int:member_id>/` | `access:member_detail` | Роль, состояние и право на push |
| `/statistics/` | `catalog:statistics` | Агрегаты и распределение по репозиториям, ролям, проектам |

Поиск: `/repositories/search/?q=lab&visibility=private`.
Параметр `user_id` оставляет репозитории, где у пользователя нет активной
записи доступа; отозванный доступ не исключает репозиторий из результатов.
Форма сохраняет введённые значения. До отправки фильтров показана только
форма. `%`, `_` и обратная косая черта в имени ищутся как буквальные символы.

Статистика: `/statistics/?min_members=1` показывает репозитории, у которых
активных участников **больше** одного. `LEFT JOIN` сохраняет репозитории
с нулевым количеством участников. Отозванные доступы не попадают в активные
счётчики и распределение ролей, но присутствуют в общем числе доступов.
Статистика пустой базы возвращает нули и понятные пустые состояния.

Постраничный список: `/repositories/?page=2`.
Номер страницы и порог статистики проверяются до SQL: целые числа до 1000000,
страницы от 1, пороги от 0. Некорректные значения возвращают HTTP 400
с сообщением. Отсутствующий объект возвращает HTTP 404.

Признак `private` описывает режим Git-репозитория. Регистрация, авторизация
и изменение данных через веб-формы на этапе ПР7 не реализуются.
Все формы выше используют GET и только читают данные.

### Шаблоны и связь с ПР6

Путь данных: `URL → view → sqlite3 → SQL → SQLite → context → template → HTML`.
`db/entities.py` восстанавливает классы ПР3 из результатов JOIN для существующих
карточек. Сохраняются методы `days_since()`, `masked_url()` и `access_status()`.
Поиск, сортировка и фильтрация выполняются в SQL; классы сохраняют поведение
предметной области. Статистика и список пользователей передают `sqlite3.Row`
прямо в шаблон. View больше не вызывают JSON-загрузчики.
`catalog/data.py` сохранён как прежний JSON-адаптер ПР5–ПР6.

Общий `templates/base.html` содержит блоки `title` и `content`, навигация
включается из `templates/includes/navigation.html`. Шаблоны приложений
находятся в `homepage/templates/homepage`, `catalog/templates/catalog`
и `access/templates/access`. Сохранены extends, include, if, for, empty,
фильтры length/default/date и именованные ссылки через url с namespace.
Автоматическое экранирование Django включено.

Ресурсы `homepage/static/homepage/`: `css/style.css`, `img/logo.svg`,
`js/main.js`. Они подключаются через static. CSS оформляет карточки,
формы, статистику, статусы и мобильную версию; JS обновляет год в подвале.
Bootstrap 5.3.3 подключён через CDN, собственные стили работают без него.

### Проверки и режим отладки

```bash
python manage.py check
python -m pytest -v
python -m flake8
python -m mypy main.py storage.py utils.py models db
python manage.py findstatic homepage/css/style.css homepage/js/main.js homepage/img/logo.svg
```

Результат ПР7: 97 тестов проходят; Django check, flake8 и mypy — без ошибок.
52 проверки ПР3–ПР6 сохранены (веб-фикстура адаптирована к временной SQLite).
45 новых проверок охватывают 18 запросов, внешние ключи, уникальность,
повторный импорт и откат, SQL-фильтрацию, статистику, NULL, защиту параметров,
пустую базу и независимость веб-интерфейса от JSON. Тесты используют временные
файлы, учебные JSON и основная база не изменяются.

`DEBUG=True` по умолчанию: runserver раздаёт статику автоматически.
Для проверки собственной 404 с оформлением (macOS/Linux):

```bash
DJANGO_DEBUG=0 python manage.py runserver --insecure
```

В PowerShell: `$env:DJANGO_DEBUG="0"`, затем та же команда runserver.
Проверьте `/missing/` и `/repositories/999/`.
`handler404` рендерит `404.html` со статусом 404. `--insecure` нужен только
для локальной проверки статики при отключённой отладке.
Для развёртывания статика собирается через `python manage.py collectstatic`;
`STATIC_ROOT=staticfiles/` исключён из Git. Секрет задаётся переменной
`DJANGO_SECRET_KEY`; локальные настройки не предназначены для публикации.

### Git и учебные материалы

Изменения ПР5–ПР7 подготовлены в рабочем каталоге без автоматического коммита.
База `data/repo_manager.sqlite` является частью сдаваемых материалов.
Для фиксации после просмотра изменений:

```bash
git status
git diff
git add manage.py config homepage catalog access templates db sql tests
git add README.md Makefile requirements.txt .gitignore data/repo_manager.sqlite
git add ПР7_отчет_Челышев_ЭФБО-10-24.docx
git commit -m "PR7: add SQLite storage and SQL web features"
```

Материалы раздела 05 Яндекс Практикума: реляционные базы, SQLite и SQL,
запросы из Python, SELECT, WHERE, сортировка, LIMIT/OFFSET, агрегатные функции
и GROUP BY. Их прохождение подтверждается отдельно в личном аккаунте.
В ПР9 переход на Django ORM выполнен; подробности приведены выше.
