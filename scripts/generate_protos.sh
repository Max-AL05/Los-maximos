#!/bin/bash
# Genera el código Python gRPC a partir de los .proto en /proto
# Coloca los archivos *_pb2.py y *_pb2_grpc.py dentro de cada microservicio que lo necesite

set -e
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
PROTO_DIR="$ROOT/proto"

services=(ms-auth ms-periodos ms-alumnos ms-calificaciones ms-asistencias ms-notificaciones ms-reportes)

for ms in "${services[@]}"; do
  out="$ROOT/$ms/protos"
  mkdir -p "$out"
  touch "$out/__init__.py"
  python -m grpc_tools.protoc \
    -I"$PROTO_DIR" \
    --python_out="$out" \
    --grpc_python_out="$out" \
    --pyi_out="$out" \
    "$PROTO_DIR"/*.proto
  echo "✓ Protos generados para $ms"
done

echo "Listo. Recuerda: si tu MS importa 'from protos import auth_pb2', los imports relativos ya funcionan."
