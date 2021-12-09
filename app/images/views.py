from accounts.models import Account
from django.conf import settings
from django.http import \
    HttpResponseForbidden, HttpResponseGone, FileResponse
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import viewsets
from rest_framework.decorators import api_view, permission_classes
from rest_framework.mixins import DestroyModelMixin, CreateModelMixin, ListModelMixin, RetrieveModelMixin

from .models import Image, ExpiringLink
from .serializers import ImageSerializer, ExpiringLinkSerializer


@api_view(['GET'])
@permission_classes([])
def access_expiring(request, name):
    """
    view to access image under expiring link
    """
    link = get_object_or_404(ExpiringLink, name=name)
    if link.expiring < timezone.now():
        return HttpResponseGone("Link expired")
    return FileResponse(link.image.image)


@api_view(['GET'])
def media_access(request, path):
    """
    View to access original image
    """
    access = False
    user = request.user
    image = get_object_or_404(Image, image=path)
    if user.is_staff:
        access = True
    elif image.owner == user:
        account = Account.objects.filter(user=user).first()
        perks = account.tier.perks.filter(name__exact=settings.IMAGES.get('original_image_perk', ''))
        if perks:
            access = True

    if access:
        response = FileResponse(image.image)
        return response

    return HttpResponseForbidden(f'Not authorized to access this file {user}')


@api_view(['GET'])
def get_thumbnail(request, path, height):
    """
    View to access thumbnail
    """
    access = False
    user = request.user
    image = get_object_or_404(Image, image=path)
    if user.is_staff:
        access = True
    elif image.owner == user:
        account = Account.objects.filter(user=user).first()
        perk_name = settings.IMAGES.get('height_perk_name').get(height, None)
        if perk_name:
            perk = account.tier.perks.filter(name__exact=perk_name)
            if perk:
                access = True

    if access:
        new_width = height * image.width // image.height
        thumbnail_image = image.image.field.storage.open(image.image.thumbnail[f'{height}x{new_width}'].name)
        response = FileResponse(thumbnail_image)
        return response

    return HttpResponseForbidden('Not authorized to access this file')


class CreateListDeleteRetrieveViewSet(DestroyModelMixin, CreateModelMixin,
                                      ListModelMixin, RetrieveModelMixin,
                                      viewsets.GenericViewSet):
    """
    A viewset that provides `retrieve`, `create`, 'delete' and `list` actions.

    To use it, override the class and set the `.queryset` and
    `.serializer_class` attributes.
    """
    pass


class ImageViewSet(CreateListDeleteRetrieveViewSet):
    serializer_class = ImageSerializer

    def get_queryset(self):
        return self.request.user.image_set.all()


class ExpiringLinkViewSet(CreateListDeleteRetrieveViewSet):
    serializer_class = ExpiringLinkSerializer

    def get_queryset(self):
        return ExpiringLink.objects.filter(image__owner=self.request.user)
