from django.db import models
from django.contrib.auth.models import AbstractUser

from core.managers import ExtendedUserManager


class User(AbstractUser):
    last_request = models.DateTimeField(null=True)

    objects = ExtendedUserManager()


class Post(models.Model):
    topic = models.CharField(max_length=250)
    text = models.TextField()
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts')
    users_liked = models.ManyToManyField(User, through='Like', related_name='liked_posts')
    date_created = models.DateTimeField(auto_now_add=True)


class Like(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='likes')
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='likes')
    date_created = models.DateTimeField(null=True)

    '''class Meta:
        # it is unclear can user like multiple times or not
        unique_together = ('user', 'post',)'''


