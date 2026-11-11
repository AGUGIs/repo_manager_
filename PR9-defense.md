# Repo Manager — подготовка к защите ПР9

Разбор отчёта «ПР9_отчет_Челышев_ЭФБО-10-24.docx» и ответы на все 30 заданий из таблицы оценивания в § 7.3 методички ПР9. Примеры Roomly заменены сущностями repo-manager. Ссылки ведут к файлам рабочей копии. Если вы скачали этот документ отдельно, положите его в корень repo-manager и откройте в редакторе вместе с проектом. Номер после двоеточия в подписи ссылки — строка в текущем коде.

## Как устроен проект

Проект ведёт учёт учебных проектов, их Git-репозиториев и записей о доступе. Веб-интерфейс показывает эти сведения и рассчитывает право на push по роли. Сам push выполняет Git, а здесь хранится и отображается правило. Признак `private` описывает видимость репозитория в каталоге. Пользователь проекта — запись предметной области.

**Путь запроса.** Например, `/repositories/2/` попадает через корневой маршрут в `repository_detail()`. Обработчик получает репозиторий, его проект, владельца и записи доступа через ORM. Затем он передаёт эти объекты в HTML-шаблон, который собирает карточку.

| Файл | Что находится внутри |
| --- | --- |
| [manage.py](manage.py) | Вход в команды Django. Через него запускаются сервер, shell, миграции и импорт. |
| [config/settings.py](config/settings.py) | Список приложений, поиск шаблонов, статика, режим отладки и путь к `db.sqlite3`. |
| [config/urls.py](config/urls.py) | Подключение маршрутов трёх приложений и общий обработчик 404. |
| [config/wsgi.py](config/wsgi.py), [config/asgi.py](config/asgi.py) | Точки входа для серверов WSGI и ASGI. |
| [homepage/urls.py](homepage/urls.py), [homepage/views.py](homepage/views.py) | Маршрут главной, вывод главной и страницы 404. |
| [catalog/urls.py](catalog/urls.py), [catalog/views.py](catalog/views.py) | Маршруты и обработчики списков, карточек, поиска и статистики. |
| [catalog/querying.py](catalog/querying.py), [db/parameters.py](db/parameters.py) | Получение GET-параметров, проверка чисел и допустимых значений, фильтры, сортировка, пагинация. |
| [catalog/models.py](catalog/models.py) | `Project`: название, владелец, дата открытия. `Repository`: название, проект, URL клонирования, признак приватности. Здесь же подсчёт возраста проекта и маскирование URL. |
| [access/models.py](access/models.py) | `User`: логин, имя, необязательная почта. `Member`: пользователь, репозиторий, роль и признак отзыва. `can_push()` разрешает push активным owner и maintainer. `revoke()` сохраняет отзыв, оставляя историю. |
| [access/urls.py](access/urls.py), [access/views.py](access/views.py) | Все доступы, активные доступы, карточка записи доступа и список пользователей. |
| [access/migrations/0001_initial.py](access/migrations/0001_initial.py), [catalog/migrations/0001_initial.py](catalog/migrations/0001_initial.py), [access/migrations/0002_initial.py](access/migrations/0002_initial.py) | Первая миграция access создаёт начальные модели, catalog создаёт проекты и репозитории, вторая access завершает связи и ограничение активного доступа. |
| [catalog/management/commands/import_pr7.py](catalog/management/commands/import_pr7.py) | Читает старую SQLite в режиме read-only, переносит записи с их ID и связями в новой транзакции. Повторный запуск сравнивает данные. |
| [templates/base.html](templates/base.html), [templates/includes/navigation.html](templates/includes/navigation.html), [templates/404.html](templates/404.html) | Общая оболочка сайта, меню и оформление ошибки 404. |
| [index.html](homepage/templates/homepage/index.html), [style.css](homepage/static/homepage/css/style.css), [logo.svg](homepage/static/homepage/img/logo.svg), [main.js](homepage/static/homepage/js/main.js) | Главная страница, внешний вид, логотип и обновление года в подвале. |
| [project_list.html](catalog/templates/catalog/project_list.html), [project_detail.html](catalog/templates/catalog/project_detail.html) | Список и карточка проекта. Карточка показывает владельца и репозитории проекта. |
| [repository_list.html](catalog/templates/catalog/repository_list.html), [repository_detail.html](catalog/templates/catalog/repository_detail.html), [search.html](catalog/templates/catalog/search.html), [statistics.html](catalog/templates/catalog/statistics.html) | Список репозиториев, карточка с участниками, поиск и статистика. В `catalog/templates/catalog/includes/` лежат переиспользуемые карточки, бейдж видимости, форма фильтров и пагинация. |
| [member_list.html](access/templates/access/member_list.html), [member_detail.html](access/templates/access/member_detail.html), [user_list.html](access/templates/access/user_list.html) | Списки и карточка доступа, справочник пользователей. В `access/templates/access/includes/` лежат карточка, список и подпись статуса доступа. |
| [main.py](main.py), [storage.py](storage.py), [utils.py](utils.py) | Отдельное консольное меню. Первое отвечает за действия пользователя, второе загружает и сохраняет JSON, третье проверяет ввод. |
| [models/base.py](models/base.py), [users.py](models/users.py), [projects.py](models/projects.py), [repositories.py](models/repositories.py), [members.py](models/members.py) | Обычные Python-классы консоли. `base.py` задаёт общий идентификатор, остальные модули описывают соответствующие сущности и операции над ними. |
| [data/users.json](data/users.json), [projects.json](data/projects.json), [repositories.json](data/repositories.json), [members.json](data/members.json) | Исходные записи консольной версии. Связи сохранены числовыми ID. |
| [sql/schema.sql](sql/schema.sql), [sql/queries.sql](sql/queries.sql), [db/database.py](db/database.py), [db/import_json.py](db/import_json.py), [db/entities.py](db/entities.py) | Слой ПР7: схема старой базы, 18 именованных запросов, подключение SQLite, импорт из JSON, преобразование SQL-строк в обычные Python-объекты. `catalog/data.py` — прежний адаптер чтения JSON для сайта. |
| [tests/conftest.py](tests/conftest.py), [tests/test_orm.py](tests/test_orm.py), [tests/test_web.py](tests/test_web.py), [tests/test_database.py](tests/test_database.py) | Тестовая настройка, проверки ORM и миграций, страниц и шаблонов, исходной SQL-базы. Тесты в `test_users.py`, `test_projects.py`, `test_repositories.py` и `test_members.py` проверяют консольные сущности. |
| [requirements.txt](requirements.txt), [Makefile](Makefile), [setup.cfg](setup.cfg), [README.md](README.md) | Зависимости, команды проверки, настройки инструментов и инструкция по запуску. `apps.py` в каждом приложении задаёт его конфигурацию, `__init__.py` обозначает Python-пакеты. |

`db.sqlite3` — база текущего сайта. `data/repo_manager.sqlite` — источник ПР7, `data/repo_manager_pr7_backup.sqlite` — его резервная копия. `staticfiles/` содержит собранную статику, `tmp/` — рабочие материалы отчётов. Консоль и сайт работают со своими хранилищами. Перенос данных запускается явно.

## Что подтверждает отчёт ПР9

- **Модели и связи.** Четыре модели и три применённые миграции подтверждены. У владельца может быть много проектов, у проекта много репозиториев, у репозитория много записей доступа. `Member` связывает пользователя и репозиторий и хранит роль и историю. [catalog/models.py:8](catalog/models.py#L8), [access/models.py:6](access/models.py#L6).
- **Перенос и текущие данные.** В веб-базе 3 пользователя, 2 проекта, 2 репозитория и 3 записи доступа. Импорт сохраняет ID, сопоставляет старый `repo_id` с `repository_id`, переносит даты, NULL и флаги. Откат при ошибке и повторный запуск проверяют тесты. [import_pr7.py:25](catalog/management/commands/import_pr7.py#L25), [test_orm.py:61](tests/test_orm.py#L61).
- **Проверки.** Повторно получены 114 успешных тестов. `manage.py check` прошла, `showmigrations` показывает три применённые миграции, `makemigrations --check --dry-run` сообщает об отсутствии изменений. Flake8 по исходникам приложения и тестам прошёл. Полная команда из отчёта нашла замечания в `tmp/pr9/build_report.py`.
- **Готовность к сдаче.** Изменения ПР9 находятся в рабочей копии, в проверенной истории Git отдельного коммита ПР9 нет. Прохождение Яндекс Практикума подтверждается в личном кабинете. В таблице § 7.3 есть задания на `F()` и Django Debug Toolbar. В приложении `F()` для проекции полей и Toolbar не подключены. Ниже приведены проверенный пример для shell и способ показать SQL штатными средствами Django.

## Подготовка к демонстрации

Из корня проекта с активным виртуальным окружением запустите `python manage.py runserver`. Открывайте маршруты ниже на `http://127.0.0.1:8000`. В отдельном терминале запустите `python manage.py shell` и импортируйте:

```python
from django.db.models import Count, F, Q
from access.models import Member, User
from catalog.models import Project, Repository
```

В текущем наборе репозиторий № 1 — публичный `course-notes` с одним активным доступом. № 2 — приватный `lab-python`, проект № 2 «Лабораторные работы», два активных доступа. Для CRUD используйте учебные записи из пунктов 5–7. Изменения моделей и применение новых миграций для показа делайте в копии проекта с отдельной копией базы.

## Ответы по пункту 7.3

### 1. Описание модели и параметры поля

Покажите четыре модели. На примере `User.email`: `blank=True` разрешает оставить поле пустым при валидации, `null=True` разрешает SQL NULL. У `Repository.private` значение `default=False` подставляется при создании экземпляра без этого поля. Для демонстрации в копии поменяйте `Repository.name.max_length` с 200 на 220 и создайте миграцию. Допустимая длина при валидации изменится, а миграция зафиксирует изменение определения поля. SQLite обычно не контролирует длину VARCHAR самостоятельно. [access/models.py:9](access/models.py#L9), [catalog/models.py:30](catalog/models.py#L30).

### 2. Создание связи между моделями

Откройте два `ForeignKey` в `Member`. В shell выполните `m = Member.objects.get(pk=1)`, затем `m.repository, m.user`. У каждой записи доступа ровно один репозиторий и один пользователь. При удалении репозитория через ORM `CASCADE` удалит его записи доступа. Если в копии поменять эту связь на `PROTECT`, то при наличии доступов Django запретит удаление репозитория. Именно так уже защищён пользователь в связи `Member.user`. [access/models.py:25](access/models.py#L25), [test_orm.py:45](tests/test_orm.py#L45).

### 3. Прямые и обратные связи

От записи доступа можно перейти к репозиторию через `m.repository`, а от репозитория обратно к списку доступов через `m.repository.members.all()`. Аналогично `m.user.memberships.all()` возвращает доступы пользователя. `m.repository_id` содержит только числовой ID. Если изменить `related_name='members'` на `access_records` в копии, обратное обращение станет `r.access_records.all()`. Потребуется обновить обращения в обработчиках и ORM-выражениях. [access/models.py:25](access/models.py#L25), [catalog/views.py:43](catalog/views.py#L43).

### 4. Создание и применение миграций

В копии после изменения из пункта 1 запустите `python manage.py makemigrations catalog`, затем `python manage.py migrate`. Первая команда создаёт файл с операцией `AlterField`, вторая применяет её к базе. `python manage.py showmigrations` покажет новую отметку `[X]`. Для просмотра SQL существующей миграции выполните `python manage.py sqlmigrate catalog 0001`. [catalog/models.py:32](catalog/models.py#L32), [catalog/migrations/0001_initial.py:9](catalog/migrations/0001_initial.py#L9).

### 5. Создание объекта через ORM

В shell выполните `u = User(username='demo_pr9', full_name='Черновик')`, затем `u.full_name = 'Показ ПР9'` и `u.save()`. Проверьте `User.objects.get(pk=u.pk).full_name`: вернётся «Показ ПР9», значение на момент сохранения. Для повторного показа после удаления можно использовать тот же логин. Короткий вариант `objects.create(...)` сразу создаёт запись. [access/models.py:6](access/models.py#L6), [test_orm.py:26](tests/test_orm.py#L26).

### 6. Изменение существующего объекта

Возьмите `u = User.objects.get(username='demo_pr9')` и присвойте `u.full_name = 'Обновлённое имя'`. До сохранения новый запрос `User.objects.get(pk=u.pk).full_name` вернёт старое значение. После `u.save(update_fields=['full_name'])` повторное чтение вернёт новое. В проекте так же сохраняется отдельное поле при отзыве доступа. [access/models.py:49](access/models.py#L49), [test_orm.py:26](tests/test_orm.py#L26).

### 7. Удаление объекта

Выполните `uid = u.pk`, `u.delete()` и `User.objects.filter(pk=uid).exists()`. Получите `False`. Для сравнения на новой тестовой записи можно вызвать `User.objects.filter(pk=uid).delete()` с её ID: удаление идёт через QuerySet. У пользователя с проектами или записями доступа сработает `PROTECT`. У репозитория с доступами `CASCADE` удалит связанные `Member`. [catalog/models.py:12](catalog/models.py#L12), [access/models.py:25](access/models.py#L25), [test_orm.py:26](tests/test_orm.py#L26).

### 8. QuerySet и простой фильтр

В shell сравните `list(Repository.objects.all())` и `list(Repository.objects.filter(private=True))`. Сначала увидите оба репозитория, затем только `lab-python`. Поменяйте флаг на `False` — останется `course-notes`. `filter()` уточняет выборку, а `list()` выполняет её и загружает записи. [catalog/querying.py:42](catalog/querying.py#L42).

### 9. Фильтр по связанному полю

Покажите `Repository.objects.filter(project__title__icontains='Лабораторные')` и замените строку на `'Курсовой'`. Результат переключится с `lab-python` на `course-notes`. `project__title` ведёт через связь к названию проекта, а `project_id=2` сравнивает ID прямо в записи репозитория. Действующий поиск проверяет название репозитория **или** проекта. [catalog/querying.py:43](catalog/querying.py#L43).

### 10. Несколько условий фильтрации

Откройте `/repositories/?project_id=2&visibility=private`: будет `lab-python`. Замените `private` на `public`: выдача опустеет. Условия разных фильтров объединяются через И. Для дополнительного примера добавьте `&user_id=1` к первоначальному URL: `lab-python` исключится из-за активного доступа пользователя № 1. [catalog/querying.py:46](catalog/querying.py#L46).

### 11. Проверка пользовательского ввода

Покажите `request.GET` и `integer_parameter()`. Сравните `/repositories/?project_id=2&page=1` и `/repositories/?project_id=abc`. Первая ссылка вернёт 200, вторая 400 с сообщением. Проверяются длина поисковой строки, значения режима и сортировки, числовые параметры и существование указанных проекта или пользователя. [catalog/querying.py:21](catalog/querying.py#L21), [db/parameters.py:4](db/parameters.py#L4), [catalog/views.py:35](catalog/views.py#L35).

### 12. Сортировка ORM-запроса

Сравните `/repositories/?sort=name` и `/repositories/?sort=-name`. При первом варианте `course-notes` идёт первым, при втором — `lab-python`. `Lower('name')` используется для сортировки по названию, `.desc()` меняет направление, а ID разрешает совпадения. В shell пример префикса — `Repository.objects.order_by('-id')`. [catalog/querying.py:10](catalog/querying.py#L10), [catalog/querying.py:61](catalog/querying.py#L61).

### 13. Сортировка по параметру запроса

`sort` выбирает готовое выражение из `SORTS`. В копии поменяйте значение по умолчанию в `request.GET.get('sort', 'name')` на `'newest'` и откройте `/repositories/`: первым будет репозиторий с большим ID. Явный `?sort=name` по-прежнему задаст сортировку по имени. `?sort=unknown` даст 400. Белый список ограничивает доступные поля и предотвращает ошибки ORM на неизвестных именах. [catalog/querying.py:11](catalog/querying.py#L11), [catalog/querying.py:27](catalog/querying.py#L27).

### 14. Выбор отдельных полей через values

В списке пользователей `values('id', 'username', 'full_name', 'email')` возвращает словари. В shell выполните `list(Member.objects.values('role', 'repository__name', 'user__username'))` и добавьте `'is_revoked'`: у каждого словаря появится ещё один ключ. ORM сам соединит таблицы, когда запрошены связанные поля. [access/views.py:39](access/views.py#L39).

### 15. Вычисляемое поле через annotate и F

В проекте `annotate()` используется в статистике с `Count()`. Для задания на `F()` выполните в shell следующий пример. `F` ссылается на значение поля в SQL, `annotate` даёт ему имя, а `values` включает это имя в словарь. Если заменить `F('repository__name')` на `F('repository__project__title')`, под ключом `repo_name` появится название проекта. Для такого варианта ключ логично назвать `project_title`. [catalog/views.py:71](catalog/views.py#L71), [access/views.py:39](access/views.py#L39).

```python
rows = Member.objects.annotate(
    repo_name=F('repository__name'),
    login=F('user__username'),
).values('repo_name', 'login', 'role')
print(list(rows))
```

### 16. Объект или 404

Откройте `/repositories/2/`, затем `/repositories/999999/`. `get_object_or_404(..., pk=repo_id)` превращает отсутствие записи в HTTP 404. При `DJANGO_DEBUG=0` используется общий шаблон `404.html`. [catalog/views.py:43](catalog/views.py#L43), [config/urls.py:9](config/urls.py#L9), [homepage/views.py:12](homepage/views.py#L12).

### 17. Подсчёт и условные агрегаты

Откройте `/statistics/`. Сейчас в базе два репозитория, из них один приватный, и три активных доступа. `count()` считает записи, `aggregate()` возвращает итоговый словарь, а `Count(..., filter=Q(...))` считает только строки под условием. В shell сравните `Member.objects.aggregate(n=Count('id', filter=Q(is_revoked=False)))` и вариант с `True`: выйдет 3 и 0. [catalog/views.py:77](catalog/views.py#L77).

### 18. Статистика по связанным объектам

В статистике каждому репозиторию назначается `active_count`. Сортировка `'-active_count'` выводит сначала `lab-python` (2), затем `course-notes` (1). Для сравнения в shell используйте следующий запрос и поменяйте направление. Группировка по ролям в обработчике использует `values('role').annotate(...)`. [catalog/views.py:71](catalog/views.py#L71), [catalog/views.py:87](catalog/views.py#L87).

```python
teams = Repository.objects.annotate(
    active_count=Count('members', filter=Q(members__is_revoked=False))
)
print(list(teams.order_by('active_count', 'id').values_list('name', 'active_count')))
```

### 19. Загрузка связанных объектов через select_related

В `member_queryset()` выражение `select_related('user', 'repository__project__owner')` загружает пользователя, репозиторий, проект и владельца вместе с доступом. В shell выполните `from access.views import member_queryset`, затем `print(member_queryset().filter(pk=1).query)`. Сравните с `print(Member.objects.select_related('user').filter(pk=1).query)`: во втором SQL останется соединение для пользователя. При чтении остальных связанных полей Django может выполнить отдельные запросы. В проекте число запросов проверяет тест. Для задания с вкладкой SQL в Debug Toolbar нужна отдельная настройка инструмента. [access/views.py:8](access/views.py#L8), [test_orm.py:167](tests/test_orm.py#L167).

### 20. Выборка только нужных данных

Вызовите `print(rows.query)` для примера из пункта 15. В SELECT будут имя репозитория, логин пользователя и роль. Уберите `'role'` из `values()` и сравните SQL и ключи словаря. Связанные поля из `values()` и `F()` уже входят в один запрос с JOIN. Словари возвращают готовые значения, поэтому для их чтения загрузка связанных объектов через `select_related()` не нужна. В рабочей странице пример проекции — список пользователей. [access/views.py:39](access/views.py#L39).

### 21. Передача данных в шаблон

`projects()` передаёт QuerySet под ключом `projects`. В `project_list.html` цикл проходит по этой переменной. Для демонстрации в копии переименуйте ключ в `project_items` и используйте это имя в шаблоне во всех обращениях к списку. При переименовании только ключа шаблон получит отсутствующую переменную и покажет пустое состояние. [catalog/views.py:16](catalog/views.py#L16), [project_list.html:5](catalog/templates/catalog/project_list.html#L5).

### 22. Настройка пагинации

`Paginator(items, PAGE_SIZE)` делит отсортированную выборку. Сейчас размер страницы — 20, поэтому оба репозитория на одной странице. Для показа в копии установите `PAGE_SIZE = 1`. Откройте `/repositories/?page=1` и `/repositories/?page=2`: на каждой странице будет по одному репозиторию. [catalog/querying.py:10](catalog/querying.py#L10), [catalog/querying.py:62](catalog/querying.py#L62).

### 23. Навигация по страницам

С размером страницы 1 нажмите «Далее», затем «Назад». `has_next` и `has_previous` определяют, какие ссылки выводить. На первой странице нет ссылки «Назад», на последней нет «Далее». Для `?page=3` при двух результатах обработчик вернёт 400 с сообщением «Такой страницы нет». [pagination.html:1](catalog/templates/catalog/includes/pagination.html#L1), [catalog/querying.py:63](catalog/querying.py#L63).

### 24. Сохранение GET-параметров

С размером страницы 1 откройте `/repositories/?q=-&sort=-name&page=1`. Дефис входит в оба имени. «Далее» ведёт на `?q=-&sort=-name&page=2`. Тег `querystring` сохраняет параметры текущего запроса и заменяет `page`. Новая отправка формы фильтров начинает выдачу с первой страницы. [pagination.html:3](catalog/templates/catalog/includes/pagination.html#L3), [repository_filters.html:1](catalog/templates/catalog/includes/repository_filters.html#L1).

### 25. Фильтр, сортировка и пагинация вместе

С размером страницы 1 на `/repositories/?q=-&sort=-name` увидите `lab-python`, на следующей странице — `course-notes`. Замените сортировку на `name`: порядок поменяется. Добавьте `visibility=private` и вернитесь на страницу 1: останется только `lab-python`. Порядок действий — проверка параметров, отбор, сортировка, затем выборка страницы. Совместный сценарий покрыт тестом. [catalog/querying.py:34](catalog/querying.py#L34), [test_orm.py:118](tests/test_orm.py#L118).

### 26. Сохранение объектов без связанных записей

`Repository.objects.annotate(active_count=Count('members', filter=Q(members__is_revoked=False)))` сохраняет репозитории без активных доступов и даёт им 0. Левое соединение оставляет строку репозитория. Если предварительно отфильтровать основной QuerySet через `filter(members__is_revoked=False)`, пустые команды исчезнут. Для показа используйте временный репозиторий без участников либо готовый тест, который создаёт такие данные. [catalog/views.py:71](catalog/views.py#L71), [test_orm.py:153](tests/test_orm.py#L153).

### 27. Исключение записей через exclude

На `/members/active/` работает `exclude(is_revoked=True)`: отозванные записи убираются. Поменяйте условие на `exclude(is_revoked=False)` в shell, чтобы получить только отозванные. В текущей базе результат пуст. На `/repositories/?user_id=3` видны оба репозитория, а при `user_id=1` оба исключаются: у этого пользователя есть активный доступ к обоим. [access/views.py:22](access/views.py#L22), [catalog/querying.py:53](catalog/querying.py#L53).

### 28. Ограничение количества строк

В shell сравните `list(Repository.objects.order_by('id')[:1])` и `list(Repository.objects.order_by('id')[1:2])`: вернутся первая и вторая записи соответственно. Срез превращается в ограничение SQL, а при смещении добавляется OFFSET. Рабочий список использует `Paginator` для ограничения по номеру страницы. [catalog/querying.py:61](catalog/querying.py#L61).

### 29. Одна запись через get

`Repository.objects.get(pk=2)` вернёт `lab-python`. `get(pk=999999)` вызовет `Repository.DoesNotExist`. `Member.objects.get(role='developer')` вызовет `Member.MultipleObjectsReturned`, потому что сейчас таких записей две. `filter()` в аналогичных случаях даёт пустой QuerySet или несколько записей. `get_object_or_404()` преобразует отсутствие в 404. [test_orm.py:26](tests/test_orm.py#L26), [catalog/views.py:43](catalog/views.py#L43).

### 30. Связанные модели и ORM в представлении

Покажите `project_detail()`: `select_related('owner')` загружает владельца, `item.repositories` находит репозитории проекта, `render()` передаёт результат в `project_detail.html`. В копии добавьте `.filter(private=False)` к выборке репозиториев и сравните `/projects/2/` до и после: карточка проекта и владелец останутся видны, приватный `lab-python` исчезнет из списка. Так видно, какие данные меняются от ORM-условия и какие переменные шаблон продолжает получать. [catalog/views.py:24](catalog/views.py#L24), [project_detail.html:3](catalog/templates/catalog/project_detail.html#L3), [test_web.py:37](tests/test_web.py#L37).
