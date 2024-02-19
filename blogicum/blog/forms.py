from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserChangeForm

from .models import Comment, Post


User = get_user_model()


class PostForm(forms.ModelForm):
    """Форма 'Поста'."""

    class Meta:
        model = Post
        fields = (
            'title',
            'text',
            'pub_date',
            'location',
            'category',
            'image'
        )
        widgets = {
            'pub_date': forms.DateTimeInput(
                attrs={
                    'type': 'datetime-local'
                }
            )
        }


class EditProfileForm(UserChangeForm):
    """Форма 'Редактирования профиля'."""

    class Meta:
        model = User
        fields = (
            'username',
            'first_name',
            'last_name',
            'email'
        )


class CommentForm(forms.ModelForm):
    """Форма 'Комментария'."""

    class Meta:
        model = Comment
        fields = (
            'text',
        )
