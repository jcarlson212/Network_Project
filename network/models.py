from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    username = models.CharField(max_length=30, unique=True)

class Post(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    postText = models.CharField(max_length=100)
    date = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return self.postText;

class Like(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user")
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="post")
    class Meta:
        unique_together = (("user", "post"),)
