from django.utils import timezone
from rest_framework import serializers

from .models import Image, ExpiringLink


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
        Make sure the image is in jpg/png format
        """
        if value.content_type not in ['image/jpeg', 'image/png']:
            raise serializers.ValidationError(f'{value.content_type} is not supported')
        return value


class ExpiringLinkSerializer(serializers.ModelSerializer):
    url = serializers.SerializerMethodField(read_only=True)
    created = serializers.DateTimeField(read_only=True)
    expiring = serializers.DateTimeField(read_only=True)
    seconds = serializers.IntegerField(write_only=True, max_value=100000, min_value=60)

    class Meta:
        model = ExpiringLink
        fields = ('created', 'url', 'expiring', 'image', 'seconds')

    def create(self, validated_data):
        validated_data['expiring'] = timezone.now() + timezone.timedelta(seconds=validated_data.pop('seconds'))
        return ExpiringLink.objects.create(**validated_data)

    def get_url(self, obj):
        url = self.context['request'].build_absolute_uri(obj.get_absolute_url())
        return url
