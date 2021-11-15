from rest_framework import serializers


class ImageSerializer(serializers.Serializer):
    image = serializers.ImageField(use_url=True)

    class Meta:
        fields = ['original_url']
