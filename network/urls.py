
from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("newPost", views.new_post, name="newPost"),
    path("profile/<str:pk>/", views.profile, name="profile"),
    path("unfollow", views.unfollow, name="unfollow"),
    path("follow", views.follow, name="follow"),
    path("following-profile/<str:pk>/", views.following_profile, name="following-profile"),
    # API route
    path("edit/<str:pk>", views.edit, name="edit"),
    path("post-like/<str:pk>", views.post_like, name="post-like")
]
