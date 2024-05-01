import json
from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.urls import reverse

from .models import User, Post


def index(request):
    return render(request, "network/index.html", {
        "page_name": "all_posts"
    })


def user_profile(request, user_id):
    return render(request, "network/index.html", {
        "page_name": "user_profile",
        "page_user_id": user_id
    })


def subscriptions(request):
    return render(request, "network/index.html", {
        "page_name": "subscriptions"
    })


def posts(request):

    # Return content of posts
    if request.method == "GET":
        posts = Post.objects.order_by("-timestamp").all()
        return JsonResponse([post.serialize() for post in posts], safe=False)

    # Create a new post
    elif request.method == "POST":
        
        if not request.user.is_authenticated:
            return JsonResponse({"error": "Authorization required."}, status=401)

        # Get contents of post
        data = json.loads(request.body)
        body = data.get("body", "")

        # Create a post
        post= Post(
            author=request.user,
            body=body
        )
        post.save()

        return JsonResponse({"message": "Post created successfully."}, status=201)
    
    # Post must be via GET or POST
    else:
        return JsonResponse({
            "error": "GET or POST request required."
        }, status=400)


def subscription_posts(request):

    # Return content of subscriptions
    if request.method == "GET":

        if not request.user.is_authenticated:
            return JsonResponse({"error": "Authorization required."}, status=401)

        posts = Post.objects.filter(author__readers=request.user)
        posts = posts.order_by("-timestamp").all()

        return JsonResponse([post.serialize() for post in posts], safe=False)
    
    # Subscriptions must be via GET
    else:
        return JsonResponse({
            "error": "GET request required."
        }, status=400)


def users(request, user_id):

    if request.method == "GET":

        # Query for requested user
        try:
            user = User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return JsonResponse({
                "error": f"User with id {user_id} does not exist."
            }, status=400)
        
        author = user.serialize()

        if request.user.is_authenticated:

            if user.readers.filter(pk=request.user.id).exists():
                author["is_followed"] = True
            else:
                author["is_followed"] = False

            if user == request.user:
                author["is_author_is_user"] = True
            else:
                author["is_author_is_user"] = False

        return JsonResponse(author)
    

    elif request.method == "POST":

        if not request.user.is_authenticated:
            return JsonResponse({"error": "Authorization required."}, status=401)

        # Query for requested user
        try:
            user = User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return JsonResponse({
                "error": f"User with id {user_id} does not exist."
            }, status=400)
        
        if user == request.user:
            return JsonResponse({
                "error": "User cannot follow himself."
            }, status=400)
        
        data = json.loads(request.body)
        if data.get("followed") is not None:
            if data["followed"]:
                user.readers.add(request.user)
            else:
                user.readers.remove(request.user)

        return HttpResponse(status=204)
        
    # User must be via GET or POST
    else:
        return JsonResponse({
            "error": "GET or POST request required."
        }, status=400)
    

def posts_of_user(request, user_id):

    # Return user's posts
    if request.method == "GET":

        # Query for requested user
        try:
            user = User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return JsonResponse({
                "error": f"User with id {user_id} does not exist."
            }, status=400)
        
        posts = Post.objects.filter(author=user)
        posts = posts.order_by("-timestamp").all()

        return JsonResponse([post.serialize() for post in posts], safe=False)

    # User's posts must be via GET
    else:
        return JsonResponse({
            "error": "GET request required."
        }, status=400)


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
