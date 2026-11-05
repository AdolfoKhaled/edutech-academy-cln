"""Aggregate SolicitudDeInscripcion: Value Objects, invariantes y máquina de estados."""
from datetime import date
from decimal import Decimal

import pytest

from src.domain.curso import Curso
from src.domain.errores import CursoNoDisponible, DatosInvalidos, SolicitudNoProcesable, TransicionNoPermitida
from src.domain.estudiante import Estudiante
from src.domain.solicitud import EstadoSolicitud, LineaDeSolicitud, SolicitudDeInscripcion
from src.domain.valores import Dinero, Modalidad

CLOUD = Curso("C-1", "Cloud 01", Modalidad.EN_LINEA, Decimal("566.00"))
WEB = Curso("C-2", "Desarrollo Web", Modalidad.EN_LINEA, Decimal("779.00"))
APAGADO = Curso("C-3", "Curso deshabilitado", Modalidad.EN_LINEA, Decimal("100"), habilitado=False)
ANA = Estudiante("E-1", "Ana", preferente=True)


def solicitud(autorizada=True, *cursos):
    s = SolicitudDeInscripcion.registrar("S-1", "E-1", date(2026, 11, 1), autorizada)
    for curso, lugares in cursos or ((CLOUD, 2),):
        s.agregarCurso(curso, lugares)
    return s


def cursos(*lista):
    return {c.cursoId: c for c in lista or (CLOUD, WEB, APAGADO)}


# ---------- Value Objects ----------
def test_dinero_usa_decimal_y_rechaza_float():
    assert Dinero.de(566).monto == Decimal("566.00")
    with pytest.raises(DatosInvalidos):
        Dinero(0.1)
    with pytest.raises(DatosInvalidos):
        Dinero(Decimal("-1"))


def test_dinero_suma_y_multiplica_sin_errores_de_centavos():
    assert (Dinero.de("0.10") + Dinero.de("0.20")).monto == Decimal("0.30")
    assert Dinero.de("566.00").por(3).monto == Decimal("1698.00")
    with pytest.raises(DatosInvalidos):
        Dinero.de(1) + Dinero(Decimal("1"), "USD")


@pytest.mark.parametrize("lugares", [0, -1, 11])
def test_linea_lugares_fuera_de_rango(lugares):
    with pytest.raises(DatosInvalidos):
        LineaDeSolicitud("C-1", lugares, Dinero.de(100))


def test_linea_sin_curso():
    with pytest.raises(DatosInvalidos):
        LineaDeSolicitud(" ", 1, Dinero.de(100))


def test_total_y_lugares():
    s = solicitud(True, (CLOUD, 3), (WEB, 4))
    assert s.total.monto == Decimal("4814.00")     # 566 x 3 + 779 x 4
    assert s.lugares == 7


def test_no_repite_curso():
    s = solicitud()
    with pytest.raises(DatosInvalidos, match="ya está"):
        s.agregarCurso(CLOUD, 1)


# ---------- Máquina de estados ----------
def test_registrar_inicia_en_preinscrito_con_evento():
    s = solicitud()
    assert s.estado is EstadoSolicitud.PREINSCRITO
    assert [type(e).__name__ for e in s.eventos] == ["SolicitudRegistrada"]
    assert s.accionesPermitidas == ["formalizar", "cancelar"]


def test_flujo_completo_preinscrito_inscrito_concluido():
    s = solicitud()
    evento = s.formalizar(ANA, cursos())
    assert (s.estado, s.folio, evento.total) == (EstadoSolicitud.INSCRITO, "INS-S-1", "1132.00")
    assert s.accionesPermitidas == ["concluir"]
    s.concluir()
    assert s.estado is EstadoSolicitud.CONCLUIDO
    assert s.accionesPermitidas == []
    assert [type(e).__name__ for e in s.eventos] == ["SolicitudRegistrada", "SolicitudFormalizada",
                                                     "SolicitudConcluida"]


def test_cancelar_libera_con_motivo():
    s = solicitud()
    s.cancelar("  Cambio de horario ")
    assert (s.estado, s.motivoLiberacion) == (EstadoSolicitud.LIBERADA, "Cambio de horario")


def test_cancelar_requiere_motivo():
    s = solicitud()
    with pytest.raises(DatosInvalidos):
        s.cancelar("   ")
    assert s.estado is EstadoSolicitud.PREINSCRITO


@pytest.mark.parametrize("accion", ["formalizar", "cancelar"])
def test_desde_inscrito_no_se_formaliza_ni_cancela(accion):
    s = solicitud()
    s.formalizar(ANA, cursos())
    eventos = len(s.eventos)
    with pytest.raises(TransicionNoPermitida):
        s.formalizar(ANA, cursos()) if accion == "formalizar" else s.cancelar()
    assert s.estado is EstadoSolicitud.INSCRITO and len(s.eventos) == eventos   # nada cambió


def test_no_se_salta_a_concluido():
    s = solicitud()
    with pytest.raises(TransicionNoPermitida, match="se requiere Inscrito"):
        s.concluir()


def test_estados_finales_no_aceptan_cambios():
    s = solicitud()
    s.cancelar()
    for accion in (lambda: s.formalizar(ANA, cursos()), s.concluir, s.cancelar):
        with pytest.raises(TransicionNoPermitida):
            accion()


def test_solo_preinscrito_agrega_cursos():
    s = solicitud()
    s.formalizar(ANA, cursos())
    with pytest.raises(TransicionNoPermitida):
        s.agregarCurso(WEB, 1)


# ---------- Reglas al formalizar ----------
def test_estudiante_inactivo_no_formaliza():
    s = solicitud()
    with pytest.raises(SolicitudNoProcesable, match="estudiante activo"):
        s.formalizar(Estudiante("E-1", "Ana", activo=False), cursos())
    assert s.estado is EstadoSolicitud.PREINSCRITO


def test_sin_autorizacion_no_formaliza():
    with pytest.raises(SolicitudNoProcesable, match="autorizada"):
        solicitud(False).formalizar(ANA, cursos())


def test_sin_cursos_no_formaliza():
    s = SolicitudDeInscripcion.registrar("S-2", "E-1", date(2026, 11, 1), True)
    with pytest.raises(SolicitudNoProcesable, match="al menos un curso"):
        s.formalizar(ANA, cursos())


def test_curso_deshabilitado_no_formaliza():
    s = solicitud(True, (CLOUD, 1), (APAGADO, 1))
    with pytest.raises(CursoNoDisponible, match="C-3"):
        s.formalizar(ANA, cursos())
    assert s.folio is None
