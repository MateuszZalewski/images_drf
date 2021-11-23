from accounts.models import Account
from django.http import \
    HttpResponseForbidden, JsonResponse, \
    HttpResponseBadRequest, HttpResponseGone, FileResponse
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import viewsets, status
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.mixins import DestroyModelMixin
from rest_framework.response import Response

from .models import Image, ExpiringLink
from .serializers import ImageSerializer


@api_view(['GET'])
@authentication_classes([])
@permission_classes([])
def access_expiring(request, name):
    """
    view to access image under expiring link
    """
    link = get_object_or_404(ExpiringLink, name=name)
    if link.expiring < timezone.now():
        link.delete()
        return HttpResponseGone("Link expired")
    return FileResponse(link.image.image)


@api_view(['GET'])
def fetch_expiring_link(request, path, time):
    """
    view to create expiring link. time must be between 300 and 30000
    """
    access = False
    user = request.user
    image = get_object_or_404(Image, image=path)
    if time < 300 or time > 30000:
        return HttpResponseBadRequest()
    if user.is_staff:
        access = True
    elif image.owner == user:
        account = Account.objects.filter(user=user).first()
        perks = account.tier.perks.filter(name__exact='expiring link')
        if perks:
            access = True

    if access:
        expiry_time = timezone.now() + timezone.timedelta(seconds=time)
        expiring_link = ExpiringLink.objects.create(expiring=expiry_time, image=image)
        data = {
            'link': request.build_absolute_uri(expiring_link.get_absolute_url()),
            'expires': expiring_link.expiring.strftime('%d-%m-%Y %H:%M:%S')
        }
        response = JsonResponse(data)
        return response
    return HttpResponseForbidden(f'Forbidden')


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
        perks = account.tier.perks.filter(name__exact='original image')
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
    height_perk_name = {
        200: '200px thumbnail',
        400: '400px thumbnail'
    }
    access = False
    user = request.user
    image = get_object_or_404(Image, image=path)
    if user.is_staff:
        access = True
    elif image.owner == user:
        account = Account.objects.filter(user=user).first()
        perk_name = height_perk_name[height]
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


class ImageViewSet(DestroyModelMixin, viewsets.GenericViewSet):
    """
    Images ViewSet
    """
    serializer_class = ImageSerializer

    def create(self, request):
        serializer = ImageSerializer(data=request.data, context={'user': request.user})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED
        )

    def list(self, request):
        serializer = ImageSerializer(self.get_queryset(), context={'request': request}, many=True)
        return Response(serializer.data)

    def get_queryset(self):
        return Image.objects.filter(owner=self.request.user)
