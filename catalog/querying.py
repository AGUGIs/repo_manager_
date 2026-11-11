"""Совместная обработка поиска, фильтров, сортировки и пагинации."""
from django.core.paginator import EmptyPage, Paginator
from django.db.models import Q
from django.db.models.functions import Lower

from access.models import Member, User
from db.parameters import integer_parameter
from .models import Project, Repository

PAGE_SIZE = 20
SORTS = {
    'name': (Lower('name'), 'id'),
    '-name': (Lower('name').desc(), '-id'),
    'project': ('project__title', 'id'),
    'newest': ('-id',),
}
SORT_LABELS = {'name': 'Название А–Я', '-name': 'Название Я–А',
               'project': 'Название проекта', 'newest': 'Сначала новые'}


def repository_context(request, *, searched=True):
    """Валидация входных данных до выполнения ORM-выборки."""
    query = request.GET.get('q', '').strip()
    visibility = request.GET.get('visibility', 'all')
    user = request.GET.get('user_id', '')
    project = request.GET.get('project_id', '')
    sort = request.GET.get('sort', 'name')
    context = {'query': query, 'visibility': visibility,
               'selected_user': user, 'selected_project': project,
               'sort': sort, 'sort_options': SORT_LABELS.items(),
               'projects': Project.objects.all(),
               'users': User.objects.all(), 'searched': searched,
               'error': '', 'repositories': [], 'total': 0}
    try:
        if len(query) > 200:
            raise ValueError('Название должно быть не длиннее 200 символов.')
        if visibility not in ('all', 'public', 'private'):
            raise ValueError('Выберите корректный режим доступа.')
        if sort not in SORTS:
            raise ValueError('Выберите корректную сортировку.')
        number = integer_parameter(request.GET.get('page', '1'), minimum=1)
        items = Repository.objects.select_related('project__owner')
        if query:
            items = items.filter(Q(name__icontains=query) |
                                 Q(project__title__icontains=query))
        if visibility != 'all':
            items = items.filter(private=visibility == 'private')
        if project:
            project_id = integer_parameter(project, minimum=1)
            if not Project.objects.filter(pk=project_id).exists():
                raise ValueError('Выбранный проект не найден.')
            items = items.filter(project_id=project_id)
        if user:
            user_id = integer_parameter(user, minimum=1)
            if not User.objects.filter(pk=user_id).exists():
                raise ValueError('Выбранный пользователь не найден.')
            # Один подзапрос гарантирует совместность user и is_revoked.
            assigned = Member.objects.filter(
                user_id=user_id, is_revoked=False).values('repository_id')
            items = items.exclude(pk__in=assigned)
        items = items.order_by(*SORTS[sort]) if searched else items.none()
        paginator = Paginator(items, PAGE_SIZE)
        try:
            page = paginator.page(number)
        except EmptyPage:
            raise ValueError('Такой страницы нет.') from None
        context.update(repositories=list(page.object_list), page_obj=page,
                       total=paginator.count)
    except ValueError as exc:
        context['error'] = str(exc)
    return context
