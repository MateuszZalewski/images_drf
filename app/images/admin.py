from django.contrib import admin

from .models import Image, ExpiringLink


@admin.register(Image)
class ImageAdmin(admin.ModelAdmin):
    exclude = ('width', 'height')


admin.site.register(ExpiringLink)
