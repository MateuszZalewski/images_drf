from django.db.models.signals import post_delete
from django.dispatch import receiver
from .models import Image


@receiver(post_delete, sender=Image)
def delete_files(sender, instance, using, **kwargs):
    """
    Deletes Image image renditions on post_delete.
    """
    # Deletes Thumbnails
    instance.image.delete_all_created_images()
    # Deletes Original Image
    instance.image.delete(save=False)
