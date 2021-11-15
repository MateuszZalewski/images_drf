import os

from django.db.models.signals import post_delete
from django.dispatch import receiver
from .models import Image


def _delete_file(path):
    """  Deletes file from filesystem.   """
    if os.path.isfile(path):
        os.remove(path)


@receiver(post_delete, sender=Image)
def delete_files(sender, instance, using, **kwargs):
    if instance.image:
        _delete_file(f'media/{instance.image}')
