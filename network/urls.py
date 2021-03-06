
from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("post", views.post, name="post"),
    path("profile/<username>", views.profile, name="profile"),
    path('follow', views.follow, name="follow"),
    path('unfollow', views.unfollow, name="unfollow"),
    path('like', views.like, name="like"),
    path('unlike', views.unlike, name="unlike"),
    path('getPosts/<int:start>/<int:end>', views.getPosts, name="getPosts"),
    path('getPostsProfile/<username>/<int:start>/<int:end>', views.getPostsProfile, name="getPostsProfile"),
    path('following', views.following, name="following"),
    path('getFollowing/<int:start>/<int:end>', views.getFollowing, name="getFollowing"),
    path('save', views.save, name="save"),
    path('like', views.like, name="like"),
    path('unlike', views.unlike, name="unlike")
]