from django.urls import path

from . import views
from .models import auction_listing
urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("<int:id>", views.listing, name="listing"),
    path("watchlist", views.watchlist, name="watchlist"),
    path("create", views.create, name="create"),
    path("category", views.category, name="category"),
    path("bid", views.bid, name="bid")
]
