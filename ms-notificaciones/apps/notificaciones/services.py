"""
Lógica de negocio reutilizable por REST y gRPC.

Cada función:
    1. Resuelve datos faltantes vía gRPC (ej: nombre del alumno, correo)
    2. Renderiza la plantilla
    3. Crea un registro Notificacion en estado PENDIENTE
    4. Envía con django.core.mail.send_mail
    5. Marca como ENVIADO o FALLIDO
"""
from django.core.mail import send_mail
from django.utils import timezone

from .models import Notificacion, TipoNotificacion, EstadoEnvio


def _send(notif: Notificacion):
    """Envía y actualiza el registro."""
    notif.intentos += 1
    try:
        send_mail(
            subject=notif.asunto,
            message="",  # versión texto plano
            from_email=None,
            recipient_list=[notif.destinatario_email],
            html_message=notif.cuerpo_html,
            fail_silently=False,
        )
        notif.estado = EstadoEnvio.ENVIADO
        notif.sent_at = timezone.now()
    except Exception as exc:
        notif.estado = EstadoEnvio.FALLIDO
        notif.error = str(exc)
    notif.save()
    return notif


def enviar_bienvenida(alumno_id, materia_id, clave_unica):
    # TODO: gRPC a MS-3 GetAlumnoById → email, nombre
    # TODO: renderizar plantilla bienvenida.html con Jinja2
    notif = Notificacion.objects.create(
        tipo=TipoNotificacion.BIENVENIDA,
        destinatario_email="placeholder@example.com",
        destinatario_user_id=str(alumno_id),
        asunto="Bienvenido(a) al sistema AGM",
        payload={"materia_id": str(materia_id), "clave_unica": clave_unica},
        cuerpo_html="<p>TODO: plantilla</p>",
    )
    return _send(notif)


def enviar_baja(alumno_id, docente_id, materia_id):
    # TODO: gRPC a MS-1 GetUserById(docente_id) y MS-3 GetAlumnoById(alumno_id)
    notif = Notificacion.objects.create(
        tipo=TipoNotificacion.BAJA,
        destinatario_email="placeholder@example.com",
        destinatario_user_id=str(docente_id),
        asunto="Un alumno se ha dado de baja de tu materia",
        payload={"alumno_id": str(alumno_id), "materia_id": str(materia_id)},
        cuerpo_html="<p>TODO: plantilla</p>",
    )
    return _send(notif)


def enviar_cierre_materia(materia_id):
    # TODO: gRPC a MS-3 GetAlumnosByMateria → loop de envíos
    return []


def enviar_reset_password(user_id, reset_link):
    # TODO: gRPC a MS-1 GetUserById
    notif = Notificacion.objects.create(
        tipo=TipoNotificacion.RESET_PASSWORD,
        destinatario_email="placeholder@example.com",
        destinatario_user_id=str(user_id),
        asunto="Recuperación de contraseña – AGM",
        payload={"reset_link": reset_link},
        cuerpo_html="<p>TODO: plantilla</p>",
    )
    return _send(notif)
