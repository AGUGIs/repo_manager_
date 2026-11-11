"""Маршруты участников репозиториев."""
from django.urls import path

from . import views

app_name = 'access'
urlpatterns = [
    path('active/', views.active_members, name='active_members'),
    path('users/', views.users, name='users'),
    path('', views.members, name='members'),
    path('<int:member_id>/', views.member_detail, name='member_detail'),
]
