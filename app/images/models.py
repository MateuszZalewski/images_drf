from django.db import models
from django.contrib.auth.models import User


class Image(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='original_size')
