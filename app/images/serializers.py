from rest_framework import serializers
from .models import Image


class ImageSerializer(serializers.Serializer):
    image = serializers.ImageField(use_url=True)

    class Meta:
        fields = ['image']

    def create(self, validated_data):
        validated_data['owner'] = self.context['user']
        return Image.objects.create(**validated_data)
