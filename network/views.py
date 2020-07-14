from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.http import JsonResponse

from .models import Follow, Like, Post, User

def index(request):
    posts = sorted(Post.objects.all(), key= lambda post: post.date, reverse=True)
    post_likes = []
    for post in posts:
        post_likes.append({ "post": post, "likes": len(Like.objects.filter(post=post))})
    return render(request, "network/index.html", {
        "post_likes": post_likes
    })

def getPosts(request, start, end):
    if request.method == 'GET':
        posts = sorted(Post.objects.all(), key= lambda post: post.date, reverse=True)
        if end < len(posts):
            posts = posts[start:end+1]
        else:
            posts = posts[start:len(posts)]
        post_likes = []
        for post in posts:
            post_likes.append({ 
                "post": {
                    "username": post.user.username,
                    "postText": post.postText,
                    "date": str(post.date)
                }, 
                "likes": str(len(Like.objects.filter(post=post)))
            })
        print(post_likes)
        return JsonResponse({ "post_likes": post_likes})
    else:
        return HttpResponse("wrong page")

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

def follow(request):
    if request.method == "POST":
        userFromName = request.POST["userFromName"]
        userToName = request.POST["userToName"]

        userFrom = User.objects.filter(username=userFromName)[0]
        userTo = User.objects.filter(username=userToName)[0]
        f = Follow(userFrom=userFrom, userTo=userTo)
        f.save()
        return HttpResponse("Follow success")
    else:
        return HttpResponse("Not found...")

def unfollow(request):
    if request.method == "POST":
        userFromName = request.POST["userFromName"]
        userToName = request.POST["userToName"]

        userFrom = User.objects.filter(username=userFromName)[0]
        userTo = User.objects.filter(username=userToName)[0]

        f = Follow.objects.get(userFrom=userFrom, userTo=userTo)
        f.delete()

        return HttpResponse("Unfollow success")
    else:
        return HttpResponse("Not found...")

def like(request):
    if request.method == "PUT":
        l = Like(userFrom=User.objects.filter(username=request.PUT["userFrom"])[0], userTo=User.objects.filter(username=request.PUT["userTo"])[0])
        l.save()
        return HttpResponse("Success")
    else:
        return HttpResponse("Not found")

def unlike(request):
    if request.method == "PUT":
        l = Like.objects.get(userFrom=User.objects.filter(username=request.PUT["userFrom"])[0], userTo=User.objects.filter(username=request.PUT["userTo"])[0])
        l.delete()
        return HttpResponse("Success")
    else:
        return HttpResponse("Not found")

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
        if follower.userFrom == currentUser:
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
