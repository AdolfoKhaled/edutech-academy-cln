"""Configuración leída de variables de entorno (12-Factor App): el código no cambia entre
desarrollo, Docker y producción; solo cambian las variables. Ver .env.example."""
import os
from dataclasses import dataclass, field
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]


def _roles(texto: str) -> dict[str, set[str]]:
    """'inst-1:Instructor;ce-1:ControlEscolar' -> {'inst-1': {'Instructor'}, ...}"""
    roles: dict[str, set[str]] = {}
    for par in filter(None, (p.strip() for p in texto.split(";"))):
        usuario, _, rol = par.partition(":")
        roles.setdefault(usuario.strip(), set()).add(rol.strip())
    return roles


@dataclass(frozen=True)
class Configuracion:
    database_url: str = "sqlite:///./edutech.db"
    cargar_datos_demo: bool = True
    datos_dir: Path = RAIZ / "datos"
    entorno: str = "desarrollo"
    roles: dict[str, set[str]] = field(default_factory=dict)

    @staticmethod
    def desde_entorno() -> "Configuracion":
        url = os.getenv("DATABASE_URL", "sqlite:///./edutech.db")
        if url.startswith("postgres://"):                 # Render y Heroku entregan este prefijo
            url = url.replace("postgres://", "postgresql+psycopg://", 1)
        elif url.startswith("postgresql://"):
            url = url.replace("postgresql://", "postgresql+psycopg://", 1)
        return Configuracion(
            database_url=url,
            cargar_datos_demo=os.getenv("CARGAR_DATOS_DEMO", "true").lower() in ("1", "true", "si", "sí"),
            datos_dir=Path(os.getenv("DATOS_DIR", str(RAIZ / "datos"))),
            entorno=os.getenv("APP_ENV", "desarrollo"),
            roles=_roles(os.getenv("ROLES_DEMO", "inst-1:Instructor;ce-1:ControlEscolar;"
                                                 "coord-1:CoordinacionAcademica")),
        )
