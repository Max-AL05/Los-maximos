"""URLs raíz de MS-6 Notificaciones."""
from django.contrib import admin
from django.http import JsonResponse
from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView


def health(_request):
    """Health check para readiness/liveness probes."""
    return JsonResponse({"status": "ok", "service": "ms-notificaciones"})


urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
    path("health/", health),

    # API REST de notificaciones
    path("notificaciones/", include("apps.notificaciones.urls")),
]
