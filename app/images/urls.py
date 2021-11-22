from django.urls import path
from rest_framework import routers

from .views import ImageViewSet, media_access, get_thumbnail, access_expiring, fetch_expiring_link

router = routers.SimpleRouter()
router.register(r'images', ImageViewSet, basename='images')
urlpatterns = router.urls + [
    path('media/<str:path>', media_access, name='media'),
    path('media/<str:path>/<int:height>', get_thumbnail, name='thumbnail'),
    path('media/<str:path>/expiring/<int:time>', fetch_expiring_link, name='create-expiring'),
    path('link/<str:name>', access_expiring, name='get-expiring'),
]
