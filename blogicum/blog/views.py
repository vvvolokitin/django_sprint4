from django.views.generic import (
    ListView,
    CreateView,
    UpdateView,
    DeleteView,
    DetailView,
)
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils import timezone
from django.urls import reverse_lazy
from django.http import HttpRequest, HttpResponse, Http404
from django.shortcuts import get_object_or_404, render, redirect

from .models import Category, Post, Comment
from .forms import PostForm, EditProfileForm, CommentForm
from core.constants import PAGINATE_LIMIT
from core.utils import get_paginator


class PostListView(ListView):
    """ Главная страница сайта."""

    template_name = 'blog/index.html'
    model = Post
    queryset = Post.proven_objects.all()
    ordering = '-pub_date'
    paginate_by = PAGINATE_LIMIT


class PostDetailView(DetailView):
    """Подробная информация о посте"""

    template_name = 'blog/detail.html'
    model = Post

    def get_context_data(self, **kwargs):
        if (
            self.object.is_published
            and self.object.category.is_published
            and self.object.pub_date <= timezone.now()
        ) or self.object.author == self.request.user:
            context = super().get_context_data(**kwargs)
            context['form'] = CommentForm()
            context['comments'] = (
                self.object.comments.select_related(
                    'author'
                )
            )
            return context
        raise Http404


def category_posts(request: HttpRequest, category_slug: str) -> HttpResponse:
    """
    Возвращает посты по категории.

    Возвращаемое значение:
        HttpResponse: информация о постах по запрашиваемой категории.
    """
    category = get_object_or_404(
        Category.objects.filter(
            slug=category_slug
        ),
        is_published=True
    )

    posts = category.posts.filter(
        pub_date__lte=timezone.now(),
        is_published=True
    )
    page_obj = get_paginator(posts, request.GET.get('page'))
    return render(
        request,
        'blog/category.html',
        {
            'category': category,
            'page_obj': page_obj
        }
    )


def user_profile(request, username):
    """Профиль пользотвателя."""
    profile = get_object_or_404(
        User,
        username=username
    )

    if request.user.is_authenticated and request.user.username == username:
        posts = profile.posts.all()
    else:
        posts = profile.posts.filter(
            pub_date__lte=timezone.now(),
            is_published=True
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


class PostUpdateView(LoginRequiredMixin, UpdateView):
    """Редактирование поста."""

    template_name = 'blog/create.html'
    model = Post
    form_class = PostForm

    def dispatch(self, request, *args, **kwargs):
        post = get_object_or_404(
            Post,
            pk=kwargs['pk']
        )
        if post.author != request.user:
            return redirect(
                'blog:post_detail',
                pk=post.pk
            )

        return super().dispatch(
            request,
            *args,
            **kwargs
        )


class PostDeleteView(LoginRequiredMixin, DeleteView):
    """Удаление поста."""

    template_name = 'blog/create.html'
    model = Post

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            post = get_object_or_404(
                Post,
                pk=kwargs['pk']
            )
            return redirect(
                'blog:post_detail',
                pk=post.pk
            )
        get_object_or_404(
            Post,
            pk=kwargs['pk'],
            author=request.user
        )
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return reverse_lazy(
            'blog:index'
        )


@login_required
def add_comment(request, pk):
    """Добавление комментария."""
    post = get_object_or_404(
        Post,
        pk=pk
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
        pk=pk
    )


class CommentUpdateView(LoginRequiredMixin, UpdateView):
    """Редактирование комментария."""

    template_name = 'blog/comment.html'
    model = Comment
    form_class = CommentForm
    success_url = reverse_lazy('blog:index')

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect(
                'blog:index'
            )

        get_object_or_404(
            Comment,
            pk=kwargs['pk'],
            author=request.user,
        )

        return super().dispatch(
            request,
            *args,
            **kwargs
        )


class CommentDeleteView(LoginRequiredMixin, DeleteView):
    """Удаление комментария."""

    template_name = 'blog/comment.html'
    model = Comment
    success_url = reverse_lazy('blog:index')

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect(
                'blog:index'
            )
        get_object_or_404(
            Comment,
            pk=kwargs['pk'],
            author=request.user
        )
        return super().dispatch(
            request,
            *args,
            **kwargs
        )
