from django.utils import timezone

from django.core.exceptions import ValidationError


def check_pub_date(pub_date) -> None:
    """Проверка даты публиакции."""
    if pub_date < timezone.now():
        raise ValidationError(
            'Ожидается корректная дата публиакции'
        )
