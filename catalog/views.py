"""Представления каталога на Django ORM без ручных SQL-запросов."""
from datetime import date

from django.db.models import Avg, Count, Max, Min, Q, Sum, IntegerField
from django.db.models.functions import Cast, Coalesce
from django.shortcuts import get_object_or_404, render
from django.views.decorators.http import require_safe

from access.models import Member, User
from db.parameters import integer_parameter
from .models import Project, Repository
from .querying import repository_context


@require_safe
def projects(request):
    """Проекты вместе с владельцами за один запрос."""
    return render(request, 'catalog/project_list.html', {
        'projects': Project.objects.select_related('owner'),
    })


@require_safe
def project_detail(request, project_id):
    """Карточка и обратная связь repositories."""
    item = get_object_or_404(Project.objects.select_related('owner'),
                             pk=project_id)
    return render(request, 'catalog/project_detail.html', {
        'project': item, 'age_days': item.days_since(date.today()),
        'repositories': item.repositories.select_related('project__owner'),
    })


@require_safe
def repositories(request):
    """Фильтрация, сортировка и пагинация выполняются в базе."""
    context = repository_context(request)
    return render(request, 'catalog/repository_list.html', context,
                  status=400 if context['error'] else 200)


@require_safe
def repository_detail(request, repo_id):
    """Карточка с оптимизированной выборкой участников."""
    item = get_object_or_404(
        Repository.objects.select_related('project__owner'), pk=repo_id)
    return render(request, 'catalog/repository_detail.html', {
        'repository': item,
        'members': item.members.select_related(
            'user', 'repository__project__owner'),
    })


@require_safe
def search(request):
    """Поиск по репозиторию или проекту, включая отсутствие доступа."""
    context = repository_context(request, searched=bool(request.GET))
    return render(request, 'catalog/search.html', context,
                  status=400 if context['error'] else 200)


@require_safe
def statistics(request):
    """Агрегаты, группировки и фильтрация по агрегату (HAVING)."""
    error = ''
    raw = request.GET.get('min_members', '1')
    try:
        minimum = integer_parameter(raw)
    except ValueError as exc:
        error, minimum = str(exc), 1
    teams = Repository.objects.annotate(active_count=Count(
        'members', filter=Q(members__is_revoked=False))).order_by(
            '-active_count', 'name', 'id')
    distribution = teams.aggregate(
        average=Avg('active_count'), minimum=Min('active_count'),
        maximum=Max('active_count'))
    return render(request, 'catalog/statistics.html', {
        'counts': {'users': User.objects.count(),
                   'projects': Project.objects.count()},
        'repository_summary': Repository.objects.aggregate(
            total=Count('id'),
            private_count=Coalesce(Sum(Cast('private', IntegerField())), 0),
            public_count=Count('id', filter=Q(private=False))),
        'member_summary': Member.objects.aggregate(
            total=Count('id'),
            active_count=Count('id', filter=Q(is_revoked=False)),
            revoked_count=Count('id', filter=Q(is_revoked=True))),
        'repository_statistics': teams,
        'role_statistics': list(Member.objects.exclude(is_revoked=True)
                                .values('role')
                                .annotate(member_count=Count('id'))
                                .order_by('-member_count', 'role')),
        'project_statistics': Project.objects.annotate(
            repo_count=Count('repositories')).order_by('-repo_count', 'id'),
        'popular_repositories': teams.filter(
            active_count__gt=minimum) if not error else [],
        'team_distribution': distribution,
        'min_members': raw, 'error': error,
    }, status=400 if error else 200)
