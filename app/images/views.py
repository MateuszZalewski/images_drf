from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Image
from .serializers import ImageSerializer


class ImageViewSet(viewsets.ViewSet):
    """
    A simple viewset to list all images
    """
    permission_classes = [IsAuthenticated]

    def list(self, request):
        serializer = ImageSerializer(self.get_queryset(), context={'request': request}, many=True)
        return Response(serializer.data)

    def get_queryset(self):
        return Image.objects.filter(owner=self.request.user)
