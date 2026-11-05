"""Carga el paquete de datos ficticios del profesor (datos/*.csv) pasando por las reglas de EduTech.

Cómo se traduce cada archivo (detalle en docs/architecture/mapeo_datos_profesor.md):
- actores.csv            -> Estudiante (es_preferente, activo)
- catalogo.csv           -> Curso (precio, habilitado) + un Grupo abierto por curso (cupo)
- operaciones.csv        -> SolicitudDeInscripcion en Preinscrito (equivale a SOLICITADA)
- detalle_operaciones.csv-> líneas de la solicitud (lugares por curso)

El cupo del catálogo se ajusta a INV-03: un grupo en línea admite como máximo 40 lugares."""
import csv
from dataclasses import dataclass, field
from datetime import date, datetime, timedelta
from decimal import Decimal
from pathlib import Path

from ..domain.curso import Curso
from ..domain.estudiante import Estudiante
from ..domain.grupo import Grupo
from ..domain.solicitud import SolicitudDeInscripcion
from ..domain.valores import Cupo, Modalidad

# Calendario de demostración: el catálogo no trae fechas; cada grupo tiene 10 sesiones hábiles.
INICIO_GRUPOS = datetime(2026, 11, 16, 20, 0)
SESIONES_DEMO = [INICIO_GRUPOS + timedelta(days=d) for d in (0, 1, 2, 3, 4, 7, 8, 9, 10, 11)]
MODALIDAD_CATALOGO = Modalidad.EN_LINEA        # giro del paquete: capacitación digital


@dataclass
class ReporteDeCarga:
    estudiantes: int = 0
    cursos: int = 0
    solicitudes: int = 0
    lineas: int = 0
    cuposAjustados: list[str] = field(default_factory=list)
    solicitudesSinCursos: list[str] = field(default_factory=list)


def leer(carpeta: Path, nombre: str) -> list[dict]:
    with (carpeta / nombre).open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def cargar_datos(sistema, carpeta: Path) -> ReporteDeCarga:
    r = ReporteDeCarga()
    for a in leer(carpeta, "actores.csv"):
        sistema.estudiantes.guardar(Estudiante(a["actor_id"], a["nombre"], a["es_preferente"] == "1",
                                               a["activo"] == "1", a["ciudad"]))
        r.estudiantes += 1

    for c in leer(carpeta, "catalogo.csv"):
        maximo = MODALIDAD_CATALOGO.cupoMaximo
        capacidad = int(c["capacidad_o_stock"])
        if capacidad > maximo:
            r.cuposAjustados.append(f"{c['recurso_id']}: {capacidad} -> {maximo}")
        sistema.cursos.guardar(Curso(c["recurso_id"], c["descripcion"], MODALIDAD_CATALOGO,
                                     Decimal(c["precio_mxn"]), habilitado=c["habilitado"] == "1"))
        sistema.grupos.guardar(Grupo(f"G-{c['recurso_id']}", c["recurso_id"], Cupo(min(capacidad, maximo)),
                                     list(SESIONES_DEMO)))
        r.cursos += 1

    cursos = {c.cursoId: c for c in sistema.cursos.todos()}
    lineas: dict[str, list[dict]] = {}
    for d in leer(carpeta, "detalle_operaciones.csv"):
        lineas.setdefault(d["operacion_id"], []).append(d)

    for o in leer(carpeta, "operaciones.csv"):
        s = SolicitudDeInscripcion.registrar(o["operacion_id"], o["actor_id"],
                                             date.fromisoformat(o["fecha_solicitud"]), o["autorizado"] == "1",
                                             o["promocion_activa"] == "1", o["referencia"])
        for d in lineas.get(o["operacion_id"], []):
            s.agregarCurso(cursos[d["recurso_id"]], int(d["cantidad"]))
            r.lineas += 1
        if not s.lineas:
            r.solicitudesSinCursos.append(s.solicitudId)
        sistema.solicitudes.guardar(s)
        r.solicitudes += 1
    return r


def base_vacia(sistema) -> bool:
    return not sistema.estudiantes.todos()
