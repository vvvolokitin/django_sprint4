from django.core.paginator import Paginator

from .constants import PAGINATE_LIMIT


def get_paginator(queryset, page_number):
    """Функция создания пагинатора."""
    paginator = Paginator(queryset, PAGINATE_LIMIT)
    page_obj = paginator.get_page(page_number)
    return page_obj
