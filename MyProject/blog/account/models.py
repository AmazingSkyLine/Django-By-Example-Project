import os

from django.contrib.auth.models import User
from django.db import models

from blog.settings import BASE_DIR


class Profile(models.Model):
    user = models.OneToOneField(User, related_name='profile',
                                on_delete=models.CASCADE)
    image = models.ImageField(upload_to='user/%Y/%m/%d',
                              blank=True, default=os.path.join(BASE_DIR, 'static/img/default.jpg'))
    cute_name = models.CharField(max_length=20)
    description = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.cute_name + "'s profile"
