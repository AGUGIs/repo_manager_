"""Просмотр пользователей и доступа через Django ORM."""
from django.shortcuts import get_object_or_404, render
from django.views.decorators.http import require_safe

from .models import Member, User


def member_queryset():
    """Загрузить связанные данные без N+1 запросов."""
    return Member.objects.select_related('user', 'repository__project__owner')


@require_safe
def members(request):
    """Все записи, включая историю отзывов."""
    return render(request, 'access/member_list.html', {
        'members': list(member_queryset()), 'active_only': False,
    })


@require_safe
def active_members(request):
    """Исключить отозванные доступы на уровне БД."""
    return render(request, 'access/member_list.html', {
        'members': list(member_queryset().exclude(is_revoked=True).order_by(
            'user__full_name', 'id')), 'active_only': True,
    })


@require_safe
def member_detail(request, member_id):
    """Неизвестная запись обрабатывается как 404."""
    return render(request, 'access/member_detail.html', {
        'member': get_object_or_404(member_queryset(), pk=member_id),
    })


@require_safe
def users(request):
    """values сохраняет словарный контекст списка пользователей ПР7."""
    return render(request, 'access/user_list.html', {
        'users': list(User.objects.values('id', 'username', 'full_name',
                                          'email')),
    })
