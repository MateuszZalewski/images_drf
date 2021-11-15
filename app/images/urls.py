from rest_framework import routers
from .views import ImageViewSet

router = routers.SimpleRouter()
router.register(r'images', ImageViewSet, basename='Image')
urlpatterns = router.urls