from django.db import models


# Create your models here.
class Shirt(models.Model):
    name = models.CharField(max_length=255, null=False)
    email = models.CharField(max_length=255, null=False)
    size = models.IntegerField(null=False)
