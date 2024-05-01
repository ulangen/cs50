
from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("user/<int:user_id>", views.user_profile, name="user_profile"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),

    # API Routes
    path("posts", views.posts, name="posts"),
    path("users/<int:user_id>", views.users, name="users"),
    path("users/<int:user_id>/posts", views.posts_of_user, name="posts_of_users")
]
