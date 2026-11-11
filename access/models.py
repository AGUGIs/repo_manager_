"""Пользователи и права доступа в Django ORM."""
from django.db import models
from django.db.models import Q


class User(models.Model):
    """Пользователь предметной области, не учётная запись Django Auth."""

    username = models.CharField(max_length=150, unique=True)
    full_name = models.CharField(max_length=200)
    email = models.EmailField(blank=True, null=True)

    class Meta:
        ordering = ['full_name', 'id']
        constraints = [models.CheckConstraint(
            condition=~Q(username=''), name='nonempty_username')]

    def __str__(self):
        return f'{self.full_name} ({self.username})'


class Member(models.Model):
    """Запись доступа; отозванные записи сохраняют историю участия."""

    repository = models.ForeignKey(
        'catalog.Repository', on_delete=models.CASCADE,
        related_name='members')
    user = models.ForeignKey(
        User, on_delete=models.PROTECT, related_name='memberships')
    role = models.CharField(max_length=100)
    is_revoked = models.BooleanField(default=False)

    class Meta:
        ordering = ['id']
        constraints = [models.UniqueConstraint(
            fields=['repository', 'user'], condition=Q(is_revoked=False),
            name='unique_active_access')]

    def can_push(self):
        """Сохранить правила ролей из ПР3."""
        return not self.is_revoked and self.role in {'owner', 'maintainer'}

    def access_status(self):
        """Подпись для существующих шаблонов."""
        if self.can_push():
            return 'Участник может выполнять push.'
        return 'Push для этой роли запрещён.'

    def revoke(self):
        """Сохранить отзыв в базе, не удаляя запись."""
        self.is_revoked = True
        self.save(update_fields=['is_revoked'])

    def __str__(self):
        return f'{self.user} | {self.role} | {self.repository.name}'
