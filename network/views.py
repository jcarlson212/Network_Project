from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.http import JsonResponse
import json

from .models import Follow, Like, Post, User

def index(request):
    return render(request, "network/index.html")

def following(request):
    if request.user.is_authenticated:
        return render(request, "network/following.html")
    return HttpResponse("Not signed in")

def like(request):
    if request.user.is_authenticated:
        if request.method == 'PUT':
            json_data = json.loads(str(request.body, encoding='utf-8'))
            print(json_data)
            current_username = json_data["current_username"]
            post_id = json_data["id"]

            user = User.objects.filter(username=current_username)[0]
            
            post = Post.objects.get(id=post_id)
            if len(Like.objects.filter(user=user, post=post)) == 0:
                new_like = Like(user=user, post=post)
                new_like.save()
                post.save()

            return HttpResponse(str(len(Like.objects.filter(post=post))))
 
    return HttpResponse("No such page...")

def unlike(request):
    if request.user.is_authenticated:
        if request.method == 'PUT':
            json_data = json.loads(str(request.body, encoding='utf-8'))

            current_username = json_data["current_username"]
            post_id = json_data["id"]

            user = User.objects.filter(username=current_username)[0]
            
            post = Post.objects.get(id=post_id)
            if len(Like.objects.filter(user=user, post=post)) > 0:
                like_to_remove = Like.objects.filter(user=user, post=post)[0]
                like_to_remove.delete()
            
            return HttpResponse(str(len(Like.objects.filter(post=post))))
        
        
    return HttpResponse("No such page...")


def getFollowing(request, start, end):
    if request.user.is_authenticated:
        if request.method == 'GET':
            shouldShowNext = False
            shouldShowPrev = False 
            posts = Post.objects.all()
            currentUser = User.objects.get(username=request.user.username)
            follows = Follow.objects.filter(userFrom=currentUser)
            usersFollowed = set()
            for f in follows:
                usersFollowed.add(f.userTo.username)
            followedPosts = []
            for p in posts:
                if p.user.username in usersFollowed:
                    followedPosts.append(p)
                    
            posts = sorted(followedPosts, key= lambda post: post.date, reverse=True)
            if end < len(posts) - 1:
                shouldShowNext = True
            if start > 0:
                shouldShowPrev = True

            if end < len(posts):
                posts = posts[start:end+1]
            else:
                posts = posts[start:len(posts)]
                

            post_likes = []
            for post in posts:
                isLiked = False
                if len(Like.objects.filter(user=request.user, post=post)) > 0:
                    isLiked = True
                post_likes.append({ 
                    "post": {
                        "username": post.user.username,
                        "postText": post.postText,
                        "date": str(post.date),
                        "id": str(post.id)
                    }, 
                    "likes": str(len(Like.objects.filter(post=post))),
                    "isLiked": isLiked
                })
            return JsonResponse({ 
                "post_likes": post_likes,
                "shouldShowNext": shouldShowNext,
                "shouldShowPrev": shouldShowPrev
            })

    return HttpResponse('Does not exist')

def getPosts(request, start, end):
    if request.method == 'GET':
        shouldShowNext = False
        shouldShowPrev = False 
        posts = sorted(Post.objects.all(), key= lambda post: post.date, reverse=True)

        if end < len(posts) - 1:
            shouldShowNext = True
        if start > 0:
            shouldShowPrev = True

        if end < len(posts):
            posts = posts[start:end+1]
        else:
            posts = posts[start:len(posts)]
        

        post_likes = []
        for post in posts:
            isLiked = False
            if request.user.is_authenticated:
                if len(Like.objects.filter(user=request.user, post=post)) > 0:
                    isLiked = True
            post_likes.append({ 
                "post": {
                    "username": post.user.username,
                    "postText": post.postText,
                    "date": str(post.date),
                    "id": str(post.id)
                }, 
                "likes": str(len(Like.objects.filter(post=post))),
                "isLiked": isLiked
            })
        return JsonResponse({ 
            "post_likes": post_likes,
            "shouldShowNext": shouldShowNext,
            "shouldShowPrev": shouldShowPrev
        })
    else:
        return HttpResponse("wrong page")

def getPostsProfile(request, username, start, end):
    if request.method == 'GET' and request.user.is_authenticated:
        shouldShowNext = False
        shouldShowPrev = False 
        profileUser = User.objects.get(username=username)
        posts = sorted(Post.objects.filter(user=profileUser), key= lambda post: post.date, reverse=True)

        if end < len(posts) - 1:
            shouldShowNext = True
        if start > 0:
            shouldShowPrev = True

        if end < len(posts):
            posts = posts[start:end+1]
        else:
            posts = posts[start:len(posts)]
        

        post_likes = []
        for post in posts:
            isLiked = False
            if len(Like.objects.filter(user=request.user, post=post)) > 0:
                isLiked = True
            post_likes.append({ 
                "post": {
                    "username": post.user.username,
                    "postText": post.postText,
                    "date": str(post.date),
                    "id": str(post.id)
                }, 
                "likes": str(len(Like.objects.filter(post=post))),
                "isLiked": isLiked
            })
        return JsonResponse({ 
            "post_likes": post_likes,
            "shouldShowNext": shouldShowNext,
            "shouldShowPrev": shouldShowPrev
        })
    else:
        return HttpResponse("wrong page")

def post(request):
    if request.method == "POST" and request.user.is_authenticated:
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
    if request.method == "POST" and request.user.is_authenticated:
        userFromName = request.POST["userFromName"]
        userToName = request.POST["userToName"]

        userFrom = User.objects.filter(username=userFromName)[0]
        userTo = User.objects.filter(username=userToName)[0]
        if len(Follow.objects.filter(userFrom=userFrom, userTo=userTo)) == 0:
            f = Follow(userFrom=userFrom, userTo=userTo)
            f.save()

        return HttpResponse("Follow success")
    else:
        return HttpResponse("Not found...")


def save(request):
    if request.method == "PUT" and request.user.is_authenticated:
        json_data = json.loads(str(request.body, encoding='utf-8'))

        username = json_data["username"]
        post_id = json_data["id"]

        user = User.objects.filter(username=username)[0]
        text = json_data["text"]
        post = Post.objects.get(id=post_id)
        post.postText = text
        post.save()
        return HttpResponse("success")
    else:
        return HttpResponse("No such page...")

def unfollow(request):
    if request.method == "POST" and request.user.is_authenticated:
        userFromName = request.POST["userFromName"]
        userToName = request.POST["userToName"]

        userFrom = User.objects.filter(username=userFromName)[0]
        userTo = User.objects.filter(username=userToName)[0]
        if len(Follow.objects.filter(userFrom=userFrom, userTo=userTo)) > 0:
            f = Follow.objects.get(userFrom=userFrom, userTo=userTo)
            f.delete()

        return HttpResponse("Unfollow success")
    else:
        return HttpResponse("Not found...")


def profile(request, username):
    if request.user.is_authenticated:
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
        
        followings = Follow.objects.filter(userFrom=user)
        return render(request, "network/profile.html", {
            "username": username,
            "post_likes": post_likes,
            "currentUser": currentUser,
            "followers": followers,
            "numberOfFollowers": str(len(followers)),
            "numberOfFollows": str(len(followings)),
            "isFollower": isFollower
        })
    return HttpResponse("Not signed in...")

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
