from django.db import models
from django.contrib.auth.models import AbstractUser


# project begging step, add custom User(not use auth.User)
class User(AbstractUser):
    pass


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    avatar = models.ImageField(blank=True)
