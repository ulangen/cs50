from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.db.models import Max, Count, Q

from .models import User, Listing, Category, Bid, Comment


def index(request):
    listings = Listing.objects.filter(is_active=True).annotate(last_bid_amount=Max("bids__amount"))

    return render(request, "auctions/index.html", {
        "title": "Active Listings",
        "listings": listings
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
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


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
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")


@login_required
def create(request):
    if request.method == "POST":
        # Create new listing
        listing = Listing(
            owner = User.objects.get(pk=request.user.id),
            title = request.POST["title"],
            description = request.POST["description"],
            starting_price = request.POST["starting_price"],
            image_url = request.POST["image_url"],
        )

        category_id = int(request.POST["category_id"])

        if category_id != 0:
            listing.category = Category.objects.get(pk=category_id)

        listing.save()

        return HttpResponseRedirect(reverse("listing", args=(listing.id,)))
    
    # Render listing creation page
    return render(request, "auctions/create.html", {
        "categories": Category.objects.all(),
    })


def listing(request, listing_id):
    listing = Listing.objects.get(pk=listing_id)
    bids = listing.bids.all()
    comments = listing.comments.all()

    last_bid = bids.order_by("-amount").first()

    if request.user.is_authenticated:
        user = User.objects.get(pk=request.user.id)
        last_user_bid = bids.filter(bidder=user).order_by("-amount").first()

        on_watchlist = False
        
        if user.watchlist.filter(pk=listing_id).exists():
            on_watchlist = True

        # Render listing page for authorized user
        return render(request, "auctions/listing.html", {
            "listing": listing,
            "bids": bids,
            "last_bid": last_bid,
            "last_user_bid": last_user_bid,
            "on_watchlist": on_watchlist,
            "comments": comments
        })

    # Render listing page for unauthorized user
    return render(request, "auctions/listing.html", {
        "listing": listing,
        "bids": bids,
        "last_bid": last_bid,
        "comments": comments
    })


@login_required
def bet(request, listing_id):
    if request.method == "POST":
        # Place bid
        listing = Listing.objects.get(pk=listing_id)
        last_bid_amount = listing.starting_price

        last_bid = listing.bids.order_by("-amount").first()

        if last_bid:
            last_bid_amount = last_bid.amount

        bid_amount = int(request.POST["bid_amount"])

        if bid_amount <= last_bid_amount:
            # Render bid error page
            return render(request, "auctions/error.html", {
                "listing": listing,
                "title": "Incorrect bid amount",
                "message": "Your bid amount must be greater than the current listing price"
            })
        
        Bid(
            bidder=User.objects.get(pk=request.user.id),
            amount=bid_amount,
            listing=listing
        ).save()
            
        return HttpResponseRedirect(reverse("listing", args=(listing.id,)))


@login_required
def close(request, listing_id):
    # Close auction
    listing = Listing.objects.get(pk=listing_id)
    listing.is_active = False
    listing.save()

    return HttpResponseRedirect(reverse("listing", args=(listing.id,)))


@login_required
def comment(request, listing_id):
    if request.method == "POST":
        # Leave comment
        user = User.objects.get(pk=request.user.id)
        listing = Listing.objects.get(pk=listing_id)
        text = request.POST["text"]

        Comment(
            author=user,
            listing=listing,
            text=text
        ).save()

        return HttpResponseRedirect(reverse("listing", args=(listing.id,)))
    

@login_required
def watchlist(request):
    user = User.objects.get(pk=request.user.id)

    if request.method == "POST":
        # Add or remove listing from watchlist
        listing = Listing.objects.get(pk=request.POST["listing_id"])

        if user.watchlist.filter(pk=listing.id).exists():
            user.watchlist.remove(listing)
        else:
            user.watchlist.add(listing)

        return HttpResponseRedirect(reverse("listing", args=(listing.id,)))
    
    listings = user.watchlist.annotate(last_bid_amount=Max("bids__amount"))
    
    # Render watchlist page
    return render(request, "auctions/index.html", {
            "title": "Watchlist",
            "listings": listings
        })


def categories(request):
    categories = Category.objects.annotate(number_of_listings=Count("listings", filter=Q(listings__is_active=True)))
    number_of_listing_without_category = Listing.objects.filter(is_active=True, category=None).count()

    # Render page with categories
    return render(request, "auctions/categories.html", {
        "categories": categories,
        "number_of_listing_without_category": number_of_listing_without_category
    })


def category(request, category_id):
    if category_id == 0:
        # Show listings without category
        listings = Listing.objects.filter(category=None, is_active=True).annotate(last_bid_amount=Max("bids__amount"))

        return render(request, "auctions/index.html", {
            "title": "No category",
            "listings": listings
        })
    
    category = Category.objects.get(pk=category_id)
    listings = category.listings.filter(is_active=True).annotate(last_bid_amount=Max("bids__amount"))

    # Render page with listings from category
    return render(request, "auctions/index.html", {
            "title": category.name,
            "listings": listings
        })
