from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import redirect


class UserTestCastomMixin(LoginRequiredMixin, UserPassesTestMixin):
    """
    Миксин проверки пользователя.

    Проверка пользователя и реализация редиректа.
    """

    def test_func(self):
        return self.get_object().author == self.request.user

    def handle_no_permission(self):
        return redirect(
            'blog:post_detail',
            post_id=self.get_object().pk
        )
