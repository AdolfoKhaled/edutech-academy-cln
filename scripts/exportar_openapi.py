"""Escribe la especificación OpenAPI de la API en docs/api/openapi.json.

Uso:  python scripts/exportar_openapi.py"""
import json
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))

from src.api.main import crear_app  # noqa: E402
from src.config import Configuracion  # noqa: E402

destino = RAIZ / "docs" / "api" / "openapi.json"
destino.parent.mkdir(parents=True, exist_ok=True)
esquema = crear_app(Configuracion(database_url="sqlite://")).openapi()
destino.write_text(json.dumps(esquema, ensure_ascii=False, indent=2), encoding="utf-8")
print(f"OpenAPI {esquema['info']['version']}: {len(esquema['paths'])} rutas -> {destino.relative_to(RAIZ)}")
