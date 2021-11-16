from django.db import models
from django.contrib.auth.models import User
from django.utils.deconstruct import deconstructible
from uuid import uuid4
import os


@deconstructible
class UploadToPathAndRename(object):
    def __init__(self, path):
        self.sub_path = path

    def __call__(self, instance, filename):
        extension = filename.split('.')[-1]
        filename = f'{str(uuid4())}.{extension}'
        return os.path.join(self.sub_path, filename)


class Image(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    image = models.ImageField(upload_to=UploadToPathAndRename(''))

    def __str__(self):
        return self.image.name
