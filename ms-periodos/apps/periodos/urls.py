from rest_framework.routers import DefaultRouter
from .views import PeriodoViewSet

router = DefaultRouter()
router.register(r"", PeriodoViewSet, basename="periodos")
urlpatterns = router.urls
