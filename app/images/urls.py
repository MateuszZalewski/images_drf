from django.urls import path
from rest_framework import routers

from .views import ImageViewSet, media_access, get_thumbnail, \
    access_expiring, ExpiringLinkViewSet

router = routers.DefaultRouter()
router.register(r'images', ImageViewSet, basename='images')
router.register(r'expiring', ExpiringLinkViewSet, basename='expiring')
urlpatterns = router.urls + [
    path('media/<str:path>', media_access, name='media'),
    path('media/<str:path>/<int:height>', get_thumbnail, name='thumbnail'),
    path('link/<str:name>', access_expiring, name='get-expiring'),
]
