from rest_framework import routers
from .views import ImageViewSet, media_access
from django.urls import path, include

router = routers.SimpleRouter()
router.register(r'images', ImageViewSet, basename='Image')
urlpatterns = router.urls + [
    path('media/<str:path>', media_access, name='media'),
]
