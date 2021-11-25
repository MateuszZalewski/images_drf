from rest_framework import serializers

from .models import Image


class ImageSerializer(serializers.Serializer):
    pk = serializers.PrimaryKeyRelatedField(read_only=True)
    image = serializers.ImageField(use_url=True)

    class Meta:
        fields = '__all__'

    def create(self, validated_data):
        validated_data['owner'] = self.context['request'].user
        return Image.objects.create(**validated_data)

    def validate_image(self, value):
        """
        Make sure the image is jpg/png format
        """
        if value.content_type not in ['image/jpeg', 'image/png']:
            raise serializers.ValidationError(f'{value.content_type} is not supported')
        return value
