"""SolicitudService con base de datos: reserva de lugares, transacciones y consultas."""
import os
from datetime import date

import pytest

from src.application.solicitud_service import RegistrarSolicitud
from src.config import Configuracion
from src.domain.errores import DatosInvalidos, NoEncontrado, SinCupo
from src.domain.grupo import Grupo
from src.domain.valores import Cupo
from src.infrastructure.carga_csv import SESIONES_DEMO


def test_formalizar_reserva_los_lugares_en_el_grupo(sistema_demo):
    antes = len(sistema_demo.grupos.obtener("G-EDU-P009").ocupados)
    s = sistema_demo.solicitud.formalizar("EDU-O001")           # P009 x3 y P014 x4
    assert s.estado.value == "Inscrito"
    assert len(sistema_demo.grupos.obtener("G-EDU-P009").ocupados) == antes + 3
    assert len(sistema_demo.grupos.obtener("G-EDU-P014").ocupados) == 4


def test_sin_cupo_revierte_toda_la_transaccion(sistema_demo):
    sistema_demo.grupos.guardar(Grupo("G-EDU-P014", "EDU-P014", Cupo(2), list(SESIONES_DEMO)))   # solo 2 lugares
    with pytest.raises(SinCupo):
        sistema_demo.solicitud.formalizar("EDU-O001")             # pide 4 de P014
    assert sistema_demo.solicitudes.obtener("EDU-O001").estado.value == "Preinscrito"
    assert sistema_demo.grupos.obtener("G-EDU-P009").ocupados == []   # el primer curso también se revirtió


def test_registrar_nueva_solicitud(sistema_demo):
    s = sistema_demo.solicitud.registrar(RegistrarSolicitud("EDU-C005", [("EDU-P001", 2), ("EDU-P002", 1)],
                                                            date(2026, 11, 5)))
    assert (s.solicitudId, str(s.total.monto), s.estado.value) == ("SOL-0061", "1769.00", "Preinscrito")
    assert sistema_demo.solicitudes.obtener("SOL-0061").lugares == 3


def test_registrar_con_estudiante_o_curso_inexistente(sistema_demo):
    with pytest.raises(NoEncontrado):
        sistema_demo.solicitud.registrar(RegistrarSolicitud("NADIE", [("EDU-P001", 1)], date(2026, 11, 5)))
    with pytest.raises(NoEncontrado):
        sistema_demo.solicitud.registrar(RegistrarSolicitud("EDU-C001", [("EDU-X", 1)], date(2026, 11, 5)))
    assert len(sistema_demo.solicitudes.todas()) == 60               # nada quedó guardado


def test_registrar_lugares_invalidos(sistema_demo):
    with pytest.raises(DatosInvalidos):
        sistema_demo.solicitud.registrar(RegistrarSolicitud("EDU-C001", [("EDU-P001", 0)], date(2026, 11, 5)))


def test_listar_por_estado(sistema_demo):
    sistema_demo.solicitud.cancelar("EDU-O002", "Prueba")
    assert [s.solicitudId for s in sistema_demo.solicitud.listar("liberada")] == ["EDU-O002"]
    assert len(sistema_demo.solicitud.listar("Preinscrito")) == 59
    assert len(sistema_demo.solicitud.listar()) == 60


def test_evaluar_no_modifica(sistema_demo):
    ev = sistema_demo.solicitud.evaluar("EDU-O013")
    assert (ev.puedeProcesarse, ev.motivos, ev.total) == (False, ["solicitud con al menos un curso"], "0.00")
    assert sistema_demo.solicitudes.obtener("EDU-O013").estado.value == "Preinscrito"


# ---------- Configuración por variables de entorno (12-Factor) ----------
def test_configuracion_desde_entorno(monkeypatch):
    monkeypatch.setenv("DATABASE_URL", "postgres://u:p@db:5432/edutech")
    monkeypatch.setenv("CARGAR_DATOS_DEMO", "false")
    monkeypatch.setenv("APP_ENV", "produccion")
    monkeypatch.setenv("ROLES_DEMO", "inst-9:Instructor; coord-9:CoordinacionAcademica")
    c = Configuracion.desde_entorno()
    assert c.database_url == "postgresql+psycopg://u:p@db:5432/edutech"
    assert (c.cargar_datos_demo, c.entorno) == (False, "produccion")
    assert c.roles == {"inst-9": {"Instructor"}, "coord-9": {"CoordinacionAcademica"}}


def test_configuracion_por_defecto(monkeypatch):
    for v in ("DATABASE_URL", "CARGAR_DATOS_DEMO", "APP_ENV", "ROLES_DEMO", "DATOS_DIR"):
        monkeypatch.delenv(v, raising=False)
    c = Configuracion.desde_entorno()
    assert c.database_url.startswith("sqlite") and c.cargar_datos_demo
    assert c.roles["coord-1"] == {"CoordinacionAcademica"}
    monkeypatch.setenv("DATABASE_URL", "postgresql://u:p@h/db")
    assert Configuracion.desde_entorno().database_url == "postgresql+psycopg://u:p@h/db"


# ---------- Mismo comportamiento en PostgreSQL (se ejecuta en Docker Compose y en CI) ----------
@pytest.mark.skipif(not os.getenv("TEST_DATABASE_URL"), reason="requiere TEST_DATABASE_URL (PostgreSQL)")
def test_postgresql_formaliza_y_revierte():
    from src.infrastructure.carga_csv import cargar_datos
    from src.infrastructure.sql import metadata
    from src.sistema import Sistema
    from tests.apoyo import DATOS
    url = os.environ["TEST_DATABASE_URL"].replace("postgresql://", "postgresql+psycopg://", 1)
    s = Sistema({}, url)
    metadata.drop_all(s.db.engine)
    metadata.create_all(s.db.engine)
    cargar_datos(s, DATOS)
    assert s.db.engine.dialect.name == "postgresql"
    assert s.solicitud.formalizar("EDU-O001").estado.value == "Inscrito"
    s.grupos.guardar(Grupo("G-EDU-P002", "EDU-P002", Cupo(1), list(SESIONES_DEMO)))
    with pytest.raises(SinCupo):
        s.solicitud.formalizar("EDU-O002")                          # pide 2 lugares de P002
    assert s.solicitudes.obtener("EDU-O002").estado.value == "Preinscrito"
    s.cerrar()
