import json
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.db.models import Exists, OuterRef, Count
from django.core.paginator import Paginator
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

@login_required
def subscriptions(request):
    return render(request, "network/index.html", {
        "page_name": "subscriptions"
    })


def serialize_page_object(page_object):
    return {
        "current": page_object.number,
        "has_next": page_object.has_next(),
        "has_previous": page_object.has_previous(),
        "divider": page_object.paginator.ELLIPSIS,
        "page_range": list(
            page_object.paginator.get_elided_page_range(
                page_object.number, on_each_side=1, on_ends=0
            )
        )
    }


def create_posts_payload(user, posts, page_number, per_page, startswith):

    # Create pagination
    paginator = Paginator(posts, per_page)
    page_object = paginator.get_page(page_number)

    # Count the number of likes on a post
    posts =  page_object.object_list
    posts = posts.annotate(
        number_of_likes=Count("liked_by")
    )

    # Serialize posts
    serialized_posts = []
    if user.is_authenticated:
        # Find out if the user liked post
        posts = posts.annotate(
            is_liked=Exists(
                user.liked_posts.filter(id=OuterRef('pk'))
            )
        )
        
        for post in posts:
            serialized_post = post.serialize()
            serialized_post["is_liked"] = post.is_liked
            serialized_post["number_of_likes"] = post.number_of_likes
            serialized_posts.append(serialized_post)
    else:
        for post in posts:
            serialized_post = post.serialize()
            serialized_post["number_of_likes"] = post.number_of_likes
            serialized_posts.append(serialized_post)

    # Serialize pagination
    page = serialize_page_object(page_object)
    page["startswith"] = startswith

    return {
        "page": page,
        "data": serialized_posts
    }


def posts(request):

    # Return content of posts
    if request.method == "GET":
        page_number = int(request.GET.get("page", 1))
        per_page = int(request.GET.get("per_page", 10))

        startswith = int(
            request.GET.get(
                "startswith",
                Post.objects.latest("id").id
            )
        )

        posts = Post.objects.filter(pk__lte=startswith).order_by("-timestamp")
        payload = create_posts_payload(request.user, posts, page_number, per_page, startswith)

        return JsonResponse(payload)

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
        
        page_number = int(request.GET.get("page", 1))
        per_page = int(request.GET.get("per_page", 10))

        startswith = int(
            request.GET.get(
                "startswith",
                Post.objects.latest("id").id
            )
        )

        posts = Post.objects.filter(author__readers=request.user)
        posts = posts.filter(pk__lte=startswith)
        posts = posts.order_by("-timestamp")

        payload = create_posts_payload(request.user, posts, page_number, per_page, startswith)

        return JsonResponse(payload)
    
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
        
        page_number = int(request.GET.get("page", 1))
        per_page = int(request.GET.get("per_page", 10))

        startswith = int(
            request.GET.get(
                "startswith",
                Post.objects.latest("id").id
            )
        )

        posts = Post.objects.filter(author=user)
        posts = posts.filter(pk__lte=startswith).order_by("-timestamp")

        payload = create_posts_payload(request.user, posts, page_number, per_page, startswith)

        return JsonResponse(payload)

    # User's posts must be via GET
    else:
        return JsonResponse({
            "error": "GET request required."
        }, status=400)


def post(request, post_id):

    # Update post contents
    if request.method == "PUT":

        if not request.user.is_authenticated:
            return JsonResponse({"error": "Authorization required."}, status=401)

        # Query for requested post
        try:
            post = Post.objects.get(pk=post_id)
        except Post.DoesNotExist:
            return JsonResponse({"error": "Post not found."}, status=404)

        data = json.loads(request.body)
        if data.get("body") is not None:

            if post.author != request.user:
                 return JsonResponse({"error": "User cannot edit other people's posts."}, status=403)

            post.body = data["body"]

        if data.get("liked") is not None:
            if data["liked"]:
                post.liked_by.add(request.user)
            else:
                post.liked_by.remove(request.user)

        post.save()
        return HttpResponse(status=204)

    # Post must be via PUT
    else:
        return JsonResponse({
            "error": "PUT request required."
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
