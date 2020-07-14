from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

from .models import Follow, Like, Post, User

def index(request):
    posts = sorted(Post.objects.all(), key= lambda post: post.date, reverse=True)
    post_likes = []
    for post in posts:
        post_likes.append({ "post": post, "likes": len(Like.objects.filter(post=post))})
    return render(request, "network/index.html", {
        "post_likes": post_likes
    })

def post(request):
    if request.method == "POST":
        username = request.user.username
        postText = request.POST["postText"]
        user = User.objects.filter(username=username)[0]

        post = Post(user=user, postText=postText)
        post.save()
        print(Post.objects.all())

        return HttpResponseRedirect(reverse('index'))
    else:
        return HttpResponse("No such page")

def profile(request, username):
    user = User.objects.filter(username=username)[0]
    posts = Post.objects.filter(user=user)
    post_likes = []
    for post in posts:
        post_likes.append({ "post": post, "likes": len(Like.objects.filter(post=post))})
    currentUser = User.objects.filter(username=request.user.username)[0]
    followers = Follow.objects.filter(userTo=user)
    isFollower = False
    for follower in followers:
        if follower == currentUser:
            isFollower = True
            break
    return render(request, "network/profile.html", {
        "username": username,
        "post_likes": post_likes,
        "currentUser": currentUser,
        "followers": followers,
        "isFollower": isFollower
    })

def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "network/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "network/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "network/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "network/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "network/register.html")
