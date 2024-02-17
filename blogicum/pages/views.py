from django.views.generic import TemplateView
from django.shortcuts import render


class AboutView(TemplateView):
    """Информация о проекте."""

    template_name: str = 'pages/about.html'


class RulesView(TemplateView):
    """Правила проекта."""

    template_name: str = 'pages/rules.html'


def page_not_found(requst, exception):
    return render(
        requst,
        'pages/404.html',
        {'path': requst.path},
        status=404
    )


def page_error(requst):
    return render(
        requst,
        'pages/500.html',
        status=500
    )


def csrf_failure(request, reason=''):
    return render(
        request,
        'pages/403csrf.html',
        status=403
    )
