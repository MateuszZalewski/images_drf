from rest_framework import routers
from .views import ImageViewSet, media_access, get_thumbnail
from django.urls import path

router = routers.SimpleRouter()
router.register(r'images', ImageViewSet, basename='images')
urlpatterns = router.urls + [
    path('media/<str:path>', media_access, name='media'),
    path('media/<str:path>/<int:height>', get_thumbnail, name='thumbnail')
]
