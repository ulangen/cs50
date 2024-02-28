from django.contrib import admin

from .models import User, Category, Listing, Comment, Bid


# Register your models here.
class UserAdmin(admin.ModelAdmin):
    list_display = ("id", "username")


class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name",)


class ListingAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "title",
        "owner",
        "starting_price",
        "category",
        "is_active"
    )
    
    filter_horizontal = ("watchers",)


class CommentAdmin(admin.ModelAdmin):
    list_display = ("id", "text", "author", "listing")


class BidAdmin(admin.ModelAdmin):
    list_display = ("id", "bidder", "listing", "amount")


admin.site.register(User, UserAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Listing, ListingAdmin)
admin.site.register(Comment, CommentAdmin)
admin.site.register(Bid, BidAdmin)
