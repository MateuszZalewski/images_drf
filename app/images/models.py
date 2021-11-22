import os
from uuid import uuid4

from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone
from django.utils.deconstruct import deconstructible
from versatileimagefield.fields import VersatileImageField


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
    image = VersatileImageField(upload_to=UploadToPathAndRename(''), height_field='height', width_field='width')
    width = models.PositiveIntegerField(blank=True, null=True)
    height = models.PositiveIntegerField(blank=True, null=True)

    def __str__(self):
        return self.image.name


class ExpiringLink(models.Model):
    image = models.ForeignKey(Image, on_delete=models.CASCADE)
    created = models.DateTimeField(default=timezone.now)
    expiring = models.DateTimeField()

    def __str__(self):
        return f'{self.image} link expiring in {self.expiring}'

    def get_period(self):
        return self.expiring - self.created
