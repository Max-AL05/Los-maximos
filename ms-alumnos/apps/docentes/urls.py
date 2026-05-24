from rest_framework.routers import DefaultRouter
from .views import DocenteViewSet

router = DefaultRouter()
router.register(r"", DocenteViewSet, basename="docentes")
urlpatterns = router.urls
