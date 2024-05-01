from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    authors = models.ManyToManyField("User", related_name="readers")

    def serialize(self):
        return {
            "id": self.id,
            "username": self.username,
            "authors": self.authors.count(),
            "readers": self.readers.count()
        }


class Post(models.Model):
    author = models.ForeignKey("User", on_delete=models.CASCADE, related_name="posts")
    body = models.TextField(blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def serialize(self):
        return {
            "id": self.id,
            "author_id": self.author.id,
            "author": self.author.username,
            "body": self.body,
            "timestamp": self.timestamp.strftime("%b %d %Y, %I:%M %p"),
        }
