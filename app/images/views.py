from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Image
from .serializers import ImageSerializer


class ImageViewSet(viewsets.ViewSet):
    """
    A simple viewset to list all images
    """
    permission_classes = [IsAuthenticated]
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
