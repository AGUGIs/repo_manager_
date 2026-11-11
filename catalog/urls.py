"""Именованные URL проектов и репозиториев."""
from django.urls import path

from . import views

app_name = 'catalog'
urlpatterns = [
    path('statistics/', views.statistics, name='statistics'),
    path('repositories/search/', views.search, name='search'),
    path('projects/', views.projects, name='projects'),
    path('projects/<int:project_id>/', views.project_detail,
         name='project_detail'),
    path('repositories/', views.repositories, name='repositories'),
    path('repositories/<int:repo_id>/', views.repository_detail,
         name='repository_detail'),
]
