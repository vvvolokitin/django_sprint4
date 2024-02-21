from django.db import models
from django.db.models.query import QuerySet
from django.utils import timezone


class PublishedCreatedModel(models.Model):
    """
    Абстрактная модель.

    Добвляет is_published и created_at.
    """

    is_published = models.BooleanField(
        default=True,
        verbose_name='Опубликовано',
        help_text='Снимите галочку, чтобы скрыть публикацию.'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Добавлено'
    )

    class Meta:
        abstract = True


class PublishedPostManager(models.Manager):
    """
    Абстрактная модель.

    Возвращает опубликованные посты.
    """

    def get_queryset(self) -> QuerySet:
        return super().get_queryset().filter(
            pub_date__lte=timezone.now(),
            is_published=True,
            category__is_published=True
        )
