"""
Cliente gRPC de prueba para MS-7 Reportes.
Llama a GenerateReport y guarda el archivo en disco.

Uso:
    python test_grpc_client.py
"""
import os
import sys

# Agregar la carpeta protos/ al path para los imports de pb2
BASE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(BASE, "protos"))

import grpc
from protos import reportes_pb2, reportes_pb2_grpc


def pedir_reporte(tipo: str, formato: str, materia_id: str = "abc"):
    print(f"\n→ Pidiendo {tipo}/{formato} por gRPC ...")
    with grpc.insecure_channel("localhost:50057") as channel:
        stub = reportes_pb2_grpc.ReportesServiceStub(channel)
        req = reportes_pb2.GenerateReportRequest(
            tipo=tipo, formato=formato, materia_id=materia_id,
        )
        resp = stub.GenerateReport(req)

    out = f"grpc_{tipo.lower()}.{formato.lower()}"
    with open(out, "wb") as f:
        f.write(resp.file_bytes)
    print(f"  ✓ {len(resp.file_bytes):>6} bytes  →  {out}")
    print(f"    file_name: {resp.file_name}")
    print(f"    mime_type: {resp.mime_type}")


if __name__ == "__main__":
    pedir_reporte("CALIFICACIONES", "PDF")
    pedir_reporte("CALIFICACIONES", "XLSX")
    pedir_reporte("ASISTENCIAS", "PDF")
    pedir_reporte("ASISTENCIAS", "XLSX")
    print("\n✓ gRPC OK")