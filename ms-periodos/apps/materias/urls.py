from rest_framework.routers import DefaultRouter
from .views import MateriaViewSet

router = DefaultRouter()
router.register(r"", MateriaViewSet, basename="materias")
urlpatterns = router.urls
