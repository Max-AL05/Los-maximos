from django.contrib import admin
from .models import Notificacion


@admin.register(Notificacion)
class NotificacionAdmin(admin.ModelAdmin):
    list_display = ("tipo", "destinatario_email", "estado", "created_at", "sent_at")
    list_filter = ("tipo", "estado")
    search_fields = ("destinatario_email",)
    readonly_fields = ("created_at", "sent_at")
