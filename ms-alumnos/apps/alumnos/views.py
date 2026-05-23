"""
Views REST de Alumnos.

Endpoints:
    POST   /alumnos/importar/<materia_id>      (Excel/CSV/PDF con vista previa)
    GET    /alumnos/materia/<materia_id>
    DELETE /alumnos/<id>/baja                  (irreversible, notifica al docente)
"""
import io
import re
import secrets
import string

import openpyxl
import pdfplumber
from django.conf import settings
from django.db import transaction
from django.utils import timezone
from rest_framework import status
from rest_framework.decorators import api_view, parser_classes, permission_classes
from rest_framework.parsers import MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Alumno, InscripcionMateria
from .serializers import AlumnoSerializer, ImportarAlumnosSerializer


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def _generar_clave_unica(longitud: int = 10) -> str:
    """Genera una clave alfanumérica aleatoria."""
    alfabeto = string.ascii_letters + string.digits
    return "".join(secrets.choice(alfabeto) for _ in range(longitud))


def _correo_desde_matricula(matricula: str) -> str:
    """
    Si el PDF institucional no trae correo, lo derivamos de la matrícula
    siguiendo la convención BUAP: <matricula>@alumno.buap.mx
    """
    return f"{matricula}@alumno.buap.mx"


def _crear_credencial_ms1(matricula: str, correo: str, nombre_completo: str, clave: str):
    """Crea el usuario en MS-1 vía REST. Devuelve user_id o None."""
    try:
        import requests
        url = "http://ms-auth:8001/auth/register"
        if hasattr(settings, "REST_URL_AUTH"):
            url = f"{settings.REST_URL_AUTH}/auth/register"
        resp = requests.post(
            url,
            json={
                "email":           correo,
                "password":        clave,
                "role":            "ALUMNO",
                "nombre_completo": nombre_completo,
                "matricula":       matricula,
            },
            timeout=10,
        )
        if resp.status_code in (200, 201):
            return resp.json().get("data", {}).get("id")
    except Exception:
        pass
    return None


def _enviar_bienvenida_ms6(alumno_id: str, materia_id: str, clave: str):
    """Notifica a MS-6 vía gRPC para enviar correo de bienvenida."""
    try:
        import grpc
        from protos import notificaciones_pb2, notificaciones_pb2_grpc
        target = settings.GRPC_TARGETS["notificaciones"]
        with grpc.insecure_channel(target) as channel:
            stub = notificaciones_pb2_grpc.NotificacionesServiceStub(channel)
            stub.SendBienvenida(
                notificaciones_pb2.SendBienvenidaRequest(
                    alumno_id=str(alumno_id),
                    materia_id=str(materia_id),
                    clave_unica=clave,
                )
            )
    except Exception:
        pass


def _enviar_baja_ms6(alumno_id: str, docente_id: str, materia_id: str):
    """Notifica a MS-6 vía gRPC la baja de un alumno."""
    try:
        import grpc
        from protos import notificaciones_pb2, notificaciones_pb2_grpc
        target = settings.GRPC_TARGETS["notificaciones"]
        with grpc.insecure_channel(target) as channel:
            stub = notificaciones_pb2_grpc.NotificacionesServiceStub(channel)
            stub.SendBajaNotif(
                notificaciones_pb2.SendBajaRequest(
                    alumno_id=str(alumno_id),
                    docente_id=str(docente_id),
                    materia_id=str(materia_id),
                )
            )
    except Exception:
        pass


def _docente_de_materia(materia_id: str) -> str | None:
    """Pregunta a MS-2 vía gRPC quién es el docente de la materia."""
    try:
        import grpc
        from protos import periodos_pb2, periodos_pb2_grpc
        target = settings.GRPC_TARGETS["periodos"]
        with grpc.insecure_channel(target) as channel:
            stub = periodos_pb2_grpc.PeriodosServiceStub(channel)
            resp = stub.GetMateriaById(
                periodos_pb2.GetMateriaByIdRequest(materia_id=str(materia_id))
            )
            return resp.docente_id or None
    except Exception:
        return None


# ---------------------------------------------------------------------------
# Parsers
# ---------------------------------------------------------------------------
def _parsear_excel(archivo):
    """
    Parsea un Excel con columnas: Matrícula | Nombre completo | Correo | Tipo (opcional)
    """
    wb = openpyxl.load_workbook(io.BytesIO(archivo.read()), data_only=True)
    ws = wb.active

    filas = []
    errores = []

    for idx, fila in enumerate(ws.iter_rows(min_row=2, values_only=True), start=2):
        if not fila or all(c is None for c in fila):
            continue
        valores = [str(c).strip() if c is not None else "" for c in fila]
        if len(valores) < 3:
            errores.append({"fila": idx, "error": "Faltan columnas (se requieren al menos 3)"})
            continue

        matricula = valores[0]
        nombre    = valores[1]
        correo    = valores[2]
        tipo      = valores[3] if len(valores) > 3 else ""

        if not matricula or not nombre or not correo:
            errores.append({"fila": idx, "error": "Campos obligatorios vacíos"})
            continue
        if "@" not in correo:
            errores.append({"fila": idx, "error": f"Correo inválido: {correo}"})
            continue

        filas.append({
            "matricula":       matricula,
            "nombre_completo": nombre,
            "correo":          correo,
            "tipo_formacion":  tipo,
        })

    return filas, errores


# Patrones para parsear el PDF del "Resumen de lista de clase" de BUAP
_RE_MATRICULA = re.compile(r"\b(2\d{8})\b")           # ej. 202224429
_RE_NIVEL     = re.compile(r"\b(Licenciatura|Maestria|Maestría|Doctorado|Posgrado)\b", re.I)


def _parsear_pdf_lista_clase(archivo):
    """
    Parsea el PDF generado por el sistema escolar de BUAP
    ("Resumen de lista de clase").

    Estrategia: por cada fila buscamos una matrícula (9 dígitos que inicia en 2).
    El nombre es lo que está antes de la matrícula. Como no hay correo en el PDF,
    lo derivamos de la convención: <matricula>@alumno.buap.mx
    """
    filas = []
    errores = []
    vistas = set()

    with pdfplumber.open(archivo) as pdf:
        for num_pag, pagina in enumerate(pdf.pages, start=1):
            # Intentar tabla primero
            tabla = pagina.extract_table()
            if tabla:
                for fila in tabla:
                    if not fila:
                        continue
                    texto_fila = " ".join(str(c).strip() if c else "" for c in fila)
                    _procesar_linea_pdf(texto_fila, filas, vistas, errores, num_pag)
            else:
                texto = pagina.extract_text() or ""
                for linea in texto.split("\n"):
                    _procesar_linea_pdf(linea, filas, vistas, errores, num_pag)

    return filas, errores


def _procesar_linea_pdf(linea: str, filas: list, vistas: set, errores: list, pagina: int):
    """
    Procesa una línea de texto del PDF.
    Espera el patrón:  [#registro]  NOMBRE APELLIDOS,...  202XXXXXXX  Inscrito  Licenciatura  6.000
    """
    m = _RE_MATRICULA.search(linea)
    if not m:
        return

    matricula = m.group(1)
    if matricula in vistas:
        return  # evita duplicados entre tabla y texto
    vistas.add(matricula)

    # El nombre es lo que está antes de la matrícula
    antes = linea[: m.start()].strip()
    # Quitar el número de registro inicial si existe (ej: "1  ", "23 ", etc.)
    antes = re.sub(r"^\s*\d{1,3}\s+", "", antes)
    nombre = antes.strip(" -:")

    if not nombre or len(nombre) < 3:
        errores.append({"fila": pagina, "error": f"No se pudo extraer el nombre para {matricula}"})
        return

    # Detectar nivel (opcional, lo guardamos como tipo_formacion)
    nivel_m = _RE_NIVEL.search(linea)
    nivel = nivel_m.group(1).capitalize() if nivel_m else ""

    filas.append({
        "matricula":       matricula,
        "nombre_completo": nombre,
        "correo":          _correo_desde_matricula(matricula),
        "tipo_formacion":  nivel,
    })


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------
@api_view(["POST"])
@parser_classes([MultiPartParser])
@permission_classes([IsAuthenticated])
def importar_alumnos(request, materia_id):
    """
    POST /alumnos/importar/<materia_id>
    Body multipart:
        - archivo_excel: archivo .xlsx o .pdf
        - confirm: "true" para guardar, ausente o "false" para solo preview
    """
    serializer = ImportarAlumnosSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    archivo = serializer.validated_data["archivo_excel"]
    confirm = str(request.data.get("confirm", "false")).lower() == "true"

    # Detectar el tipo de archivo por extensión
    nombre = (archivo.name or "").lower()
    try:
        if nombre.endswith(".pdf"):
            filas, errores = _parsear_pdf_lista_clase(archivo)
        elif nombre.endswith(".xlsx") or nombre.endswith(".xls"):
            filas, errores = _parsear_excel(archivo)
        else:
            return Response(
                {"success": False, "data": None,
                 "message": "Formato no soportado. Usa .xlsx o .pdf"},
                status=status.HTTP_400_BAD_REQUEST,
            )
    except Exception as exc:
        return Response(
            {"success": False, "data": None,
             "message": f"Error al procesar el archivo: {str(exc)}"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    # Modo preview: solo devolver lo que se importaría
    if not confirm:
        return Response({
            "success": True,
            "data": {
                "preview": filas,
                "total":   len(filas),
                "errores": errores,
            },
            "message": "Vista previa generada. Envía confirm=true para guardar.",
        })

    # Modo confirmar: crear/actualizar registros
    alumnos_creados    = 0
    alumnos_existentes = 0
    inscritos          = 0
    duplicados         = 0

    with transaction.atomic():
        for f in filas:
            alumno, created = Alumno.objects.get_or_create(
                matricula=f["matricula"],
                defaults={
                    "nombre_completo": f["nombre_completo"],
                    "correo":          f["correo"],
                    "tipo_formacion":  f["tipo_formacion"],
                },
            )

            if created:
                alumnos_creados += 1
                clave = _generar_clave_unica()
                user_id = _crear_credencial_ms1(
                    matricula=alumno.matricula,
                    correo=alumno.correo,
                    nombre_completo=alumno.nombre_completo,
                    clave=clave,
                )
                if user_id:
                    alumno.user_id = user_id
                    alumno.save(update_fields=["user_id"])
                _enviar_bienvenida_ms6(
                    alumno_id=str(alumno.id),
                    materia_id=str(materia_id),
                    clave=clave,
                )
            else:
                alumnos_existentes += 1

            _, inscrito_creado = InscripcionMateria.objects.get_or_create(
                alumno=alumno,
                materia_id=str(materia_id),
                defaults={"dado_de_baja": False},
            )
            if inscrito_creado:
                inscritos += 1
            else:
                duplicados += 1

    return Response(
        {
            "success": True,
            "data": {
                "importados":          len(filas),
                "alumnos_nuevos":      alumnos_creados,
                "alumnos_existentes":  alumnos_existentes,
                "inscripciones_nuevas": inscritos,
                "ya_inscritos":        duplicados,
                "errores":             errores,
            },
            "message": f"{inscritos} alumnos inscritos en la materia",
        },
        status=status.HTTP_201_CREATED,
    )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def alumnos_por_materia(request, materia_id):
    """GET /alumnos/materia/<materia_id>"""
    inscripciones = InscripcionMateria.objects.filter(
        materia_id=str(materia_id), dado_de_baja=False
    ).select_related("alumno")
    data = AlumnoSerializer([i.alumno for i in inscripciones], many=True).data
    return Response({"success": True, "data": data, "message": ""})


@api_view(["DELETE", "POST"])
@permission_classes([IsAuthenticated])
def baja_alumno(request, alumno_id):
    """DELETE/POST /alumnos/<alumno_id>/baja?materia_id=<uuid>"""
    materia_id = (
        request.data.get("materia_id")
        or request.query_params.get("materia_id")
    )
    if not materia_id:
        return Response(
            {"success": False, "data": None, "message": "Falta materia_id"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    try:
        inscripcion = InscripcionMateria.objects.select_related("alumno").get(
            alumno_id=alumno_id, materia_id=str(materia_id)
        )
    except InscripcionMateria.DoesNotExist:
        return Response(
            {"success": False, "data": None, "message": "El alumno no está inscrito en esa materia"},
            status=status.HTTP_404_NOT_FOUND,
        )

    if inscripcion.dado_de_baja:
        return Response(
            {"success": False, "data": None, "message": "La inscripción ya fue dada de baja"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    inscripcion.dado_de_baja = True
    inscripcion.fecha_baja = timezone.now()
    inscripcion.save(update_fields=["dado_de_baja", "fecha_baja"])

    docente_id = _docente_de_materia(str(materia_id))
    if docente_id:
        _enviar_baja_ms6(
            alumno_id=str(alumno_id),
            docente_id=docente_id,
            materia_id=str(materia_id),
        )

    return Response(
        {"success": True, "data": None, "message": "Baja registrada correctamente"},
        status=status.HTTP_200_OK,
    )