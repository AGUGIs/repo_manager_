"""Проекты и репозитории с управляемой миграциями схемой."""
from datetime import date

from django.db import models
from django.db.models.functions import Lower


class Project(models.Model):
    """Проект принадлежит одному владельцу."""

    title = models.CharField(max_length=200)
    owner = models.ForeignKey(
        'access.User', on_delete=models.PROTECT, related_name='projects')
    opened_on = models.DateField(default=date.today)

    class Meta:
        ordering = ['opened_on', 'id']

    def days_since(self, current):
        """Количество дней с открытия проекта."""
        return (current - self.opened_on).days

    def __str__(self):
        return self.title


class Repository(models.Model):
    """Репозиторий связан с проектом и участниками через Member."""

    project = models.ForeignKey(
        Project, on_delete=models.PROTECT, related_name='repositories')
    name = models.CharField(max_length=200)
    clone_url = models.URLField(max_length=500)
    private = models.BooleanField(default=False)

    class Meta:
        ordering = [Lower('name'), 'id']

    def visibility_text(self):
        """Описание режима доступа."""
        if self.private:
            return 'Доступ к репозиторию ограничен'
        return 'Репозиторий открыт для просмотра'

    def masked_url(self):
        """Сохранить представление адреса из ПР3."""
        if len(self.clone_url) < 18:
            return 'скрыто'
        return self.clone_url[:10] + '***' + self.clone_url[-8:]

    def __str__(self):
        return self.name
