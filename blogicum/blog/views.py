from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db.models import Count, Q
from django.db.models.base import Model as Model
from django.views.generic import (
    ListView,
    CreateView,
    UpdateView,
    DeleteView,
    DetailView,
)
from django.utils import timezone
from django.urls import reverse_lazy
from django.http import HttpRequest, HttpResponse, Http404
from django.shortcuts import get_object_or_404, render, redirect

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
    ).all()
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
        post = super().get_object(queryset=queryset)
        if not ((
            post.is_published
            and post.category.is_published
            and post.pub_date <= timezone.now()
        ) or post.author == self.request.user):
            raise Http404
        return post


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
    flag = ~Q(
        pk__in=[]
    )
    if request.user.is_authenticated:
        flag = Q(
            author=request.user
        )
    posts = profile.posts.filter(
        flag
        | Q(pub_date__lte=timezone.now())
        & Q(is_published=True,)
    ).annotate(
        comment_count=Count(
            'comments'
        )
    ).order_by(
        '-pub_date'
    )

    page_obj = get_paginator(posts, request.GET.get('page'))
    return render(
        request,
        'blog/profile.html',
        {
            'profile': profile,
            'page_obj': page_obj,
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


class PostUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """Редактирование поста."""

    template_name = 'blog/create.html'
    model = Post
    form_class = PostForm
    pk_url_kwarg = 'post_id'
    redirect_field_name = None
    login_url = '/'

    def get_login_url(self):
        return f'/posts/{self.get_object().pk}/'

    def test_func(self):
        return self.get_object().author == self.request.user

    def handle_no_permission(self):

        return redirect(
            'blog:post_detail',
            post_id=self.get_object().pk
        )

    def dispatch(self, request, *args, **kwargs):
        get_object_or_404(
            Post,
            pk=kwargs['post_id']
        )

        return super().dispatch(
            request,
            *args,
            **kwargs
        )

    def get_success_url(self):
        return reverse_lazy(
            'blog:post_detail',
            kwargs={
                'post_id': self.get_object().pk
            }
        )


class PostDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    """Удаление поста."""

    template_name = 'blog/create.html'
    model = Post
    pk_url_kwarg = 'post_id'
    redirect_field_name = None
    login_url = '/'

    def get_login_url(self):
        return f'/posts/{self.get_object().pk}/'

    def test_func(self):
        return self.get_object().author == self.request.user

    def handle_no_permission(self):
        return redirect(
            'blog:post_detail',
            post_id=self.get_object().pk
        )

    def dispatch(self, request, *args, **kwargs):
        get_object_or_404(
            Post,
            pk=kwargs['post_id']
        )
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return reverse_lazy(
            'blog:index'
        )


@login_required
def add_comment(request, post_id):
    """Добавление комментария."""
    post = get_object_or_404(
        Post,
        pk=post_id
    )
    form = CommentForm(
        request.POST
        or None
    )

    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect(
        'blog:post_detail',
        post_id=post_id
    )


class CommentUpdateView(LoginRequiredMixin, UpdateView):
    """Редактирование комментария."""

    template_name = 'blog/comment.html'
    model = Comment
    form_class = CommentForm
    pk_url_kwarg = 'comment_id'

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect(
                'blog:index'
            )

        get_object_or_404(
            Comment,
            pk=kwargs['comment_id'],
            author=request.user,
        )

        return super().dispatch(
            request,
            *args,
            **kwargs
        )

    def get_success_url(self):
        return reverse_lazy(
            'blog:post_detail',
            kwargs={
                'post_id': self.get_object().post.pk
            }
        )


class CommentDeleteView(LoginRequiredMixin, DeleteView):
    """Удаление комментария."""

    template_name = 'blog/comment.html'
    model = Comment
    pk_url_kwarg = 'comment_id'

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect(
                'blog:index'
            )
        get_object_or_404(
            Comment,
            pk=kwargs['comment_id'],
            author=request.user
        )
        return super().dispatch(
            request,
            *args,
            **kwargs
        )

    def get_success_url(self):
        return reverse_lazy(
            'blog:post_detail',
            kwargs={
                'post_id': self.get_object().post.pk
            }
        )
