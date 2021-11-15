from rest_framework import viewsets
from rest_framework.response import Response
from .models import Image
from .serializers import ImageSerializer


class ImageViewSet(viewsets.ViewSet):
    """
    A simple viewset to list all images
    """
    queryset = Image.objects.all()

    def list(self, request):
        queryset = Image.objects.all()
        serializer = ImageSerializer(queryset, context={'request': request}, many=True)
        return Response(serializer.data)

    def get_queryset(self):
        return Image.objects.all()
