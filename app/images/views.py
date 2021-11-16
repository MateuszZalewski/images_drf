from rest_framework import viewsets, status
from rest_framework.mixins import DestroyModelMixin
from rest_framework.response import Response
from rest_framework.decorators import api_view

from django.http import HttpResponseForbidden
from django.http.response import FileResponse

from .models import Image
from .serializers import ImageSerializer


@api_view(['GET'])
def media_access(request, path):
    user = request.user
    image = Image.objects.filter(image=path).first()
    if image.owner == user or user.is_staff:
        response = FileResponse(image.image)
        return response

    return HttpResponseForbidden(f'Not authorized to access this file')


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
        pass

    def list(self, request):
        serializer = ImageSerializer(self.get_queryset(), context={'request': request}, many=True)
        return Response(serializer.data)

    def get_queryset(self):
        return Image.objects.filter(owner=self.request.user)
