from django.contrib import admin

from .models import Image, ExpiringLink

admin.site.register(Image)
admin.site.register(ExpiringLink)
