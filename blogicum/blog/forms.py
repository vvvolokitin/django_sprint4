from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserChangeForm


from .models import Post, Comment


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

    email = forms.EmailField(
        widget=forms.EmailInput(
            attrs={
                'class': 'form-control',
                'placeholder': "Введите вашу электронную почту"
            }
        ),
        label='Электронная почта'
    )
    first_name = forms.CharField(
        widget=forms.TextInput(
            attrs={
                'class': 'form-control',
                'placeholder': "Введите ваше имя"
            }
        ),
        label='Имя',
        required=False
    )
    last_name = forms.CharField(
        widget=forms.TextInput(
            attrs={
                'class': 'form-control',
                'placeholder': "Введите вашу фамилию"
            }
        ),
        label='Фамилия',
        required=False

    )
    username = forms.CharField(
        max_length=20,
        widget=forms.TextInput(
            attrs={
                'class': 'form-control',
                'placeholder': "Введите ваш логин"
            }
        ),
        label='Логин'
    )

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
