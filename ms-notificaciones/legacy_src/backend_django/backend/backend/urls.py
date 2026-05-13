"""
URL configuration for backend project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from api import views
from api.views import crear_publicacion, crear_comentario
from api.views import lista_publicaciones
from django.conf import settings
from django.conf.urls.static import static
from api.views import registrar_mascota, registrar_mascota_encontrada, registrar_mascota_adopcion

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/register/', views.register, name='register'),
    path('api/login/', views.login, name='login'),
    path('api/change_password/', views.change_password, name='change_password'),
    path('api/registrar_mascota/', registrar_mascota, name='registrar_mascota'),
    path('api/registrar_mascota_encontrada/', registrar_mascota_encontrada, name='registrar_mascota_encontrada'),
    path('api/registrar_adopcion/', registrar_mascota_adopcion, name='registrar_adopcion'),
    path('api/crear_publicacion/', crear_publicacion, name='crear_publicacion'),
    path('api/crear_comentario/', crear_comentario, name='crear_comentario'),
    path('api/publicaciones/', lista_publicaciones, name='lista_publicaciones'),
    path('mascotas_adopcion/', registrar_mascota_adopcion, name='registrar_mascota_adopcion'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
