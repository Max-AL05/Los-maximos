from django.contrib import admin
from .models import Notificacion


@admin.register(Notificacion)
class NotificacionAdmin(admin.ModelAdmin):
    list_display = ("tipo", "destinatario_email", "estado", "intentos", "created_at", "sent_at")
    list_filter = ("tipo", "estado")
    search_fields = ("destinatario_email", "asunto")
    readonly_fields = ("id", "created_at", "sent_at", "intentos", "cuerpo_html", "payload")
    fieldsets = (
        ("Identificación", {"fields": ("id", "tipo", "estado")}),
        ("Destinatario", {"fields": ("destinatario_email", "destinatario_user_id")}),
        ("Contenido", {"fields": ("asunto", "cuerpo_html", "payload")}),
        ("Resultado", {"fields": ("intentos", "error", "created_at", "sent_at")}),
    )
