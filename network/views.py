import json
from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.urls import reverse

from .models import User, Post


def index(request):
    return render(request, "network/index.html")


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
