from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count, Q
from django.views.generic import (
    ListView,
    CreateView,
    UpdateView,
    DeleteView,
    DetailView,
)
from django.utils import timezone
from django.urls import reverse_lazy
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, render, redirect

from .mixins import UserTestCastomMixin
from .models import Category, Post, Comment
from .forms import PostForm, EditProfileForm, CommentForm
from core.constants import PAGINATE_LIMIT
from core.utils import get_paginator


class PostListView(ListView):
    """Главная страница сайта."""

    template_name = 'blog/index.html'
    model = Post
    queryset = Post.published_posts.annotate(
        comment_count=Count('comments')
    )
    ordering = '-pub_date'
    paginate_by = PAGINATE_LIMIT


class PostDetailView(DetailView):
    """Подробная информация о посте"""

    template_name = 'blog/detail.html'
    model = Post
    pk_url_kwarg = 'post_id'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = CommentForm()
        context['comments'] = (
            self.object.comments.select_related(
                'author'
            )
        )
        return context

    def get_object(self, queryset=None):
        return get_object_or_404(
            self.model.objects.filter(
                Q(author_id=self.request.user.id)
                | Q(pub_date__lte=timezone.now())
                & Q(is_published=True)
                & Q(category__is_published=True)
            ),
            pk=self.kwargs[
                self.pk_url_kwarg
            ]
        )


def category_posts(request: HttpRequest, category_slug: str) -> HttpResponse:
    """
    Возвращает посты по категории.

    Возвращаемое значение:
        HttpResponse: информация о постах по запрашиваемой категории.
    """
    category = get_object_or_404(
        Category,
        slug=category_slug,
        is_published=True
    )

    return render(
        request,
        'blog/category.html',
        {
            'category': category,
            'page_obj': get_paginator(
                category.posts.filter(
                    pub_date__lte=timezone.now(),
                    is_published=True
                ),
                request.GET.get('page')
            )
        }
    )


def user_profile(request, username):
    """Профиль пользователя."""
    profile = get_object_or_404(
        User,
        username=username
    )
    posts = profile.posts.filter(
        Q(author_id=request.user.id)
        | Q(pub_date__lte=timezone.now())
        & Q(is_published=True,)
    ).annotate(
        comment_count=Count(
            'comments'
        )
    ).order_by(
        '-pub_date'
    )

    return render(
        request,
        'blog/profile.html',
        {
            'profile': profile,
            'page_obj': get_paginator(
                posts,
                request.GET.get('page')
            ),
        }
    )


class EditProfile(LoginRequiredMixin, UpdateView):
    """Редактирование профиля пользователя."""

    template_name = 'blog/user.html'

    model = User
    form_class = EditProfileForm

    def get_object(self):
        return self.request.user

    def get_success_url(self):
        return reverse_lazy(
            'blog:profile',
            kwargs={
                'username': self.request.user
            }
        )


class PostCreateView(LoginRequiredMixin, CreateView):
    """Создание поста."""

    template_name = 'blog/create.html'
    model = Post
    form_class = PostForm

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy(
            'blog:profile',
            kwargs={
                'username': self.request.user
            }
        )


class PostUpdateView(UserTestCastomMixin, UpdateView):
    """Редактирование поста."""

    template_name = 'blog/create.html'
    model = Post
    form_class = PostForm
    pk_url_kwarg = 'post_id'

    def get_object(self, queryset=None):
        return get_object_or_404(
            self.model,
            pk=self.kwargs[
                self.pk_url_kwarg
            ],
            is_published=True
        )

    def get_success_url(self):
        return reverse_lazy(
            'blog:post_detail',
            kwargs={
                'post_id': self.get_object().pk
            }
        )


class PostDeleteView(UserTestCastomMixin, DeleteView):
    """Удаление поста."""

    template_name = 'blog/create.html'
    model = Post
    pk_url_kwarg = 'post_id'

    def get_object(self, queryset=None):
        return get_object_or_404(
            self.model,
            pk=self.kwargs[
                self.pk_url_kwarg
            ],
            is_published=True
        )

    def get_success_url(self):
        return reverse_lazy(
            'blog:index'
        )


@login_required
def add_comment(request, post_id):
    """Добавление комментария."""
    form = CommentForm(
        request.POST
        or None
    )

    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = get_object_or_404(
            Post,
            pk=post_id
        )
        comment.save()
    return redirect(
        'blog:post_detail',
        post_id=post_id
    )


class CommentUpdateView(UserTestCastomMixin, UpdateView):
    """Редактирование комментария."""

    template_name = 'blog/comment.html'
    model = Comment
    form_class = CommentForm
    pk_url_kwarg = 'comment_id'

    def handle_no_permission(self):
        return redirect(
            'blog:post_detail',
            post_id=self.get_object().post.pk
        )

    def get_object(self, queryset=None):
        return get_object_or_404(
            self.model,
            pk=self.kwargs[
                self.pk_url_kwarg
            ]
        )

    def get_success_url(self):
        return reverse_lazy(
            'blog:post_detail',
            kwargs={
                'post_id': self.get_object().post.pk
            }
        )


class CommentDeleteView(UserTestCastomMixin, DeleteView):
    """Удаление комментария."""

    template_name = 'blog/comment.html'
    model = Comment
    pk_url_kwarg = 'comment_id'

    def handle_no_permission(self):
        return redirect(
            'blog:post_detail',
            post_id=self.get_object().post.pk
        )

    def get_object(self, queryset=None):
        return get_object_or_404(
            self.model,
            pk=self.kwargs[
                self.pk_url_kwarg
            ]
        )

    def get_success_url(self):
        return reverse_lazy(
            'blog:post_detail',
            kwargs={
                'post_id': self.get_object().post.pk
            }
        )
