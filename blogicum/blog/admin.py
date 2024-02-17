from django.contrib import admin

from .models import Category, Location, Post


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = (
        'title',
        'author',
        'is_published',
        'category',
        'location'
    )
    list_editable = (
        'is_published',
        'category',
        'location'
    )
    search_fields = (
        'title',
    )
    list_filter = (
        'category',
    )
    list_display_links = (
        'title',
    )


class PostTabularInline(admin.TabularInline):
    model = Post
    extra = 0


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    inlines = (
        PostTabularInline,
    )
    list_display = (
        'title',
    )


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    inlines = (
        PostTabularInline,
    )
    list_display = (
        'name',
    )
