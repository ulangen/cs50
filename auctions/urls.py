from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("create", views.create, name="create"),
    path("listings/<int:listing_id>", views.listing, name="listing"),
    path("watchlist", views.watchlist, name="watchlist"),
    path("close/<int:listing_id>", views.close, name="close"),
    path("bet/<int:listing_id>", views.bet, name="bet"),
    path("comment/<int:listing_id>", views.comment, name="comment"),
    path("categories/<int:category_id>", views.category, name="category"),
    path("categories", views.categories, name="categories")
]
