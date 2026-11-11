"""Главная страница и обработка 404 через шаблоны Django."""
from django.shortcuts import render
from django.views.decorators.http import require_safe


@require_safe
def index(request):
    """Показать назначение приложения и переходы к данным."""
    return render(request, 'homepage/index.html')


def page_not_found(request, exception):
    """Обработать неизвестный URL или отсутствие объекта."""
    return render(request, '404.html', status=404)
