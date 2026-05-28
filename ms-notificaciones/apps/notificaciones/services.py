import logging

from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils import timezone

from .models import Notificacion, TipoNotificacion, EstadoEnvio

logger = logging.getLogger(__name__)


# ----------------------------------------------------------------------------
# Helper interno: envía y persiste resultado
# ----------------------------------------------------------------------------
def _send(notif: Notificacion):
    """Intenta enviar el correo y actualiza el estado del registro."""
    notif.intentos += 1
    try:
        send_mail(
            subject=notif.asunto,
            message="",  # versión texto plano (vacía, usamos solo HTML)
            from_email=None,  # usa DEFAULT_FROM_EMAIL
            recipient_list=[notif.destinatario_email],
            html_message=notif.cuerpo_html,
            fail_silently=False,
        )
        notif.estado = EstadoEnvio.ENVIADO
        notif.sent_at = timezone.now()
        logger.info("Email %s enviado a %s", notif.tipo, notif.destinatario_email)
    except Exception as exc:
        notif.estado = EstadoEnvio.FALLIDO
        notif.error = str(exc)
        logger.exception("Falló envío de %s a %s", notif.tipo, notif.destinatario_email)
    notif.save()
    return notif


# ----------------------------------------------------------------------------
# 1. Bienvenida (al alumno con su clave única)
# ----------------------------------------------------------------------------
def enviar_bienvenida(*, alumno_email, alumno_nombre, materia_nombre,
                      clave_unica, alumno_id=None, materia_id=None):
    contexto = {
        "alumno_nombre": alumno_nombre,
        "materia_nombre": materia_nombre,
        "clave_unica": clave_unica,
    }
    cuerpo_html = render_to_string("emails/bienvenida.html", contexto)

    notif = Notificacion.objects.create(
        tipo=TipoNotificacion.BIENVENIDA,
        destinatario_email=alumno_email,
        destinatario_user_id=str(alumno_id) if alumno_id else "",
        asunto=f"Bienvenido(a) a {materia_nombre} – AGM",
        payload={
            "alumno_nombre": alumno_nombre,
            "materia_nombre": materia_nombre,
            "materia_id": str(materia_id) if materia_id else None,
            "clave_unica": clave_unica,
        },
        cuerpo_html=cuerpo_html,
    )
    return _send(notif)


# ----------------------------------------------------------------------------
# 2. Baja (notifica al docente)
# ----------------------------------------------------------------------------
def enviar_baja(*, docente_email, docente_nombre, alumno_nombre, materia_nombre,
                motivo="", alumno_id=None, docente_id=None, materia_id=None):
    contexto = {
        "docente_nombre": docente_nombre,
        "alumno_nombre": alumno_nombre,
        "materia_nombre": materia_nombre,
        "motivo": motivo or "No especificado",
        "fecha": timezone.now().strftime("%d/%m/%Y %H:%M"),
    }
    cuerpo_html = render_to_string("emails/baja.html", contexto)

    notif = Notificacion.objects.create(
        tipo=TipoNotificacion.BAJA,
        destinatario_email=docente_email,
        destinatario_user_id=str(docente_id) if docente_id else "",
        asunto=f"Baja de alumno en {materia_nombre}",
        payload={
            "alumno_nombre": alumno_nombre,
            "alumno_id": str(alumno_id) if alumno_id else None,
            "materia_nombre": materia_nombre,
            "materia_id": str(materia_id) if materia_id else None,
            "motivo": motivo,
        },
        cuerpo_html=cuerpo_html,
    )
    return _send(notif)


# ----------------------------------------------------------------------------
# 3. Cierre de materia (envío masivo a todos los alumnos)
# ----------------------------------------------------------------------------
def enviar_cierre_materia(*, materia_nombre, alumnos, periodo="", materia_id=None):
    """
    `alumnos` es una lista de dicts: [{"email", "nombre", "calificacion_final"}, ...].
    Devuelve la lista de Notificaciones creadas.
    """
    resultados = []
    for alumno in alumnos:
        contexto = {
            "alumno_nombre": alumno["nombre"],
            "materia_nombre": materia_nombre,
            "periodo": periodo,
            "calificacion_final": alumno.get("calificacion_final"),
        }
        cuerpo_html = render_to_string("emails/cierre_materia.html", contexto)

        notif = Notificacion.objects.create(
            tipo=TipoNotificacion.CIERRE_MATERIA,
            destinatario_email=alumno["email"],
            asunto=f"Cierre de materia: {materia_nombre}",
            payload={
                "materia_nombre": materia_nombre,
                "materia_id": str(materia_id) if materia_id else None,
                "periodo": periodo,
                "calificacion_final": alumno.get("calificacion_final"),
            },
            cuerpo_html=cuerpo_html,
        )
        resultados.append(_send(notif))
    return resultados


# ----------------------------------------------------------------------------
# 4. Reset de contraseña
# ----------------------------------------------------------------------------
def enviar_reset_password(*, user_email, user_nombre, reset_link, user_id=None):
    contexto = {
        "user_nombre": user_nombre,
        "reset_link": reset_link,
    }
    cuerpo_html = render_to_string("emails/reset_password.html", contexto)

    notif = Notificacion.objects.create(
        tipo=TipoNotificacion.RESET_PASSWORD,
        destinatario_email=user_email,
        destinatario_user_id=str(user_id) if user_id else "",
        asunto="Recuperación de contraseña – AGM",
        payload={
            "user_nombre": user_nombre,
            "reset_link": reset_link,
        },
        cuerpo_html=cuerpo_html,
    )
    return _send(notif)


# ----------------------------------------------------------------------------
# 5. Reporte disponible (avisa al docente que su reporte está listo)
# ----------------------------------------------------------------------------
def enviar_reporte_disponible(*, docente_email, docente_nombre, materia_nombre,
                               tipo, formato, file_name, reporte_id=None):
    """Notifica al docente que su reporte fue generado y está disponible."""
    from django.template.loader import render_to_string
    from django.utils import timezone
    from .models import Notificacion, TipoNotificacion, EstadoEnvio

    contexto = {
        "docente_nombre": docente_nombre,
        "materia_nombre": materia_nombre,
        "tipo": tipo,
        "formato": formato,
        "file_name": file_name,
        "fecha": timezone.now().strftime("%d/%m/%Y %H:%M"),
    }
    # Reutilizamos plantilla de cierre como fallback si no existe reporte.html
    try:
        cuerpo_html = render_to_string("emails/reporte_disponible.html", contexto)
    except Exception:
        cuerpo_html = (
            f"<p>Hola {docente_nombre},</p>"
            f"<p>Tu reporte de <strong>{tipo}</strong> para la materia "
            f"<strong>{materia_nombre}</strong> en formato {formato} "
            f"ya está disponible: <code>{file_name}</code>.</p>"
        )

    notif = Notificacion.objects.create(
        tipo=TipoNotificacion.BIENVENIDA,  # reutilizamos tipo existente
        destinatario_email=docente_email,
        asunto=f"Tu reporte de {materia_nombre} está listo – AGM",
        payload={
            "tipo": tipo,
            "formato": formato,
            "materia_nombre": materia_nombre,
            "file_name": file_name,
            "reporte_id": str(reporte_id) if reporte_id else None,
        },
        cuerpo_html=cuerpo_html,
    )
    return _send(notif)
