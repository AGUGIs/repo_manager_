"""Корневая маршрутизация проекта."""
from django.urls import include, path

urlpatterns = [
    path('', include('homepage.urls')),
    path('', include('catalog.urls')),
    path('members/', include('access.urls')),
]
handler404 = 'homepage.views.page_not_found'
