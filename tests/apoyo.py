"""Datos de prueba comunes (ficticios)."""
from datetime import datetime, timedelta
from pathlib import Path

from src.domain.curso import Curso
from src.domain.grupo import Grupo
from src.domain.valores import Cupo, Modalidad
from src.sistema import Sistema

DATOS = Path(__file__).resolve().parents[1] / "datos"
INICIO = datetime(2026, 11, 2, 20, 0)          # lunes; cada sesión termina a las 20:00
SESIONES = [INICIO + timedelta(days=d) for d in (0, 1, 2, 3, 4, 7, 8, 9, 10, 11)]   # 10 sesiones hábiles
ANTES = datetime(2026, 10, 20, 10, 0)           # fecha de la solicitud de inscripción
ROLES = {"inst-1": {"Instructor"}, "inst-2": {"Instructor"}, "ce-1": {"ControlEscolar"},
         "coord-1": {"CoordinacionAcademica"}}


def datos(nombre="Ana López"):
    return {"nombre": nombre, "correo": "ana@example.com", "telefono": "8100000000"}


def sistemaConGrupo(maximo=25, sobrecupo=0, modalidad=Modalidad.PRESENCIAL):
    """Sistema completo con SQLite en memoria y un grupo G-1 de un curso de $4000."""
    s = Sistema(ROLES)
    s.cursos.guardar(Curso("C-1", "Análisis de datos", modalidad, 4000))
    s.grupos.guardar(Grupo("G-1", "C-1", Cupo(maximo, sobrecupo), list(SESIONES)))
    return s


crear_sistema = sistemaConGrupo
