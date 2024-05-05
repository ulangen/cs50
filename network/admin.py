from django.contrib import admin

from .models import User, Post


class UserAdmin(admin.ModelAdmin):
    list_display = ("username", "id", "date_joined")


class PostAdmin(admin.ModelAdmin):
    list_display = ("author", "id", "timestamp", "body")


admin.site.register(User, UserAdmin)
admin.site.register(Post, PostAdmin)
