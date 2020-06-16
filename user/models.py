from django.contrib.auth.models import AbstractUser
from django.db import models


# Create your models here.
from django.db.models import ImageField


class User(AbstractUser):
    profile_picture = ImageField(upload_to='profile-pictures/', null=True, max_length=255)
