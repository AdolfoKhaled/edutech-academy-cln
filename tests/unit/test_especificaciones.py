"""Specification Pattern: composición AND / OR / NOT y reglas del paquete y del BRD."""
from datetime import date
from decimal import Decimal

import pytest

from src.domain.curso import Curso
from src.domain.especificaciones import (
    ASISTENCIA_EN_LINEA,
    BENEFICIO_REFERENCIA,
    PUEDE_PROCESARSE,
    Autorizada,
    CandidatoSolicitud,
    ConexionEnLinea,
    EstudianteActivo,
    EstudiantePreferente,
    PromocionActiva,
    Specification,
    TieneLineas,
)
from src.domain.estudiante import Estudiante
from src.domain.solicitud import SolicitudDeInscripcion
from src.domain.valores import AsistenciaRegistrada, CriterioDeCertificacion, Modalidad


def candidato(activo=True, preferente=False, autorizada=True, promocion=False, precio="500", lugares=3):
    s = SolicitudDeInscripcion.registrar("S-1", "E-1", date(2026, 11, 1), autorizada, promocion)
    if lugares:
        s.agregarCurso(Curso("C-1", "Cloud", Modalidad.EN_LINEA, Decimal(precio)), lugares)
    return CandidatoSolicitud(s, Estudiante("E-1", "Ana", preferente, activo))


# ---------- composición ----------
def test_and_or_not_crean_reglas_compuestas():
    activo, preferente = EstudianteActivo(), EstudiantePreferente()
    c = candidato(activo=True, preferente=False)
    assert (activo & ~preferente).es_satisfecha_por(c)
    assert not (activo & preferente).es_satisfecha_por(c)
    assert (activo | preferente).es_satisfecha_por(c)
    assert not (~activo | preferente).es_satisfecha_por(c)


def test_nombres_describen_la_regla():
    assert PUEDE_PROCESARSE.nombre == ("((estudiante activo Y solicitud con al menos un curso) "
                                       "Y solicitud autorizada)")
    assert (~PromocionActiva()).nombre == "NO promoción activa"


def test_specification_base_es_abstracta():
    with pytest.raises(NotImplementedError):
        Specification().es_satisfecha_por(None)


# ---------- PUEDE_PROCESARSE (activo Y con cursos Y autorizada) ----------
def test_puede_procesarse_cuando_cumple_todo():
    assert PUEDE_PROCESARSE.es_satisfecha_por(candidato())
    assert PUEDE_PROCESARSE.incumplidas(candidato()) == []


@pytest.mark.parametrize("cambios, falta", [
    ({"activo": False}, ["estudiante activo"]),
    ({"lugares": 0}, ["solicitud con al menos un curso"]),
    ({"autorizada": False}, ["solicitud autorizada"]),
    ({"activo": False, "autorizada": False}, ["estudiante activo", "solicitud autorizada"]),
])
def test_puede_procesarse_dice_que_falta(cambios, falta):
    c = candidato(**cambios)
    assert not PUEDE_PROCESARSE.es_satisfecha_por(c)
    assert PUEDE_PROCESARSE.incumplidas(c) == falta


def test_hojas_individuales():
    c = candidato(lugares=0, autorizada=False)
    assert not TieneLineas().es_satisfecha_por(c)
    assert not Autorizada().es_satisfecha_por(c)


# ---------- BENEFICIO_REFERENCIA (preferente Y total >= 1500 Y NO promoción) ----------
@pytest.mark.parametrize("preferente, precio, lugares, promocion, esperado", [
    (True, "500", 3, False, True),        # total exactamente 1500: límite incluido
    (True, "499.99", 3, False, False),    # 1499.97: no alcanza
    (False, "1000", 3, False, False),     # no es preferente
    (True, "1000", 3, True, False),       # promoción activa
])
def test_beneficio_por_referencia(preferente, precio, lugares, promocion, esperado):
    c = candidato(preferente=preferente, precio=precio, lugares=lugares, promocion=promocion)
    assert BENEFICIO_REFERENCIA.es_satisfecha_por(c) is esperado


def test_beneficio_rechazado_explica_motivos():
    c = candidato(preferente=False, promocion=True)
    assert BENEFICIO_REFERENCIA.incumplidas(c) == ["estudiante preferente", "NO promoción activa"]


# ---------- Reglas propias de EduTech ----------
@pytest.mark.parametrize("conexion, horas, esperado", [
    (60, None, True), (59.9, None, False), (10, 72, True), (10, 72.1, False), (0, None, False)])
def test_INV12_asistencia_en_linea_es_un_OR(conexion, horas, esperado):
    assert ASISTENCIA_EN_LINEA.es_satisfecha_por(ConexionEnLinea(conexion, horas)) is esperado
    assert AsistenciaRegistrada.acreditaEnLinea(conexion, horas) is esperado


@pytest.mark.parametrize("calificacion, asistencia, esperado", [
    (70, 80, (True, None)), (69.9, 95, (False, "calificación")), (90, 79.9, (False, "asistencia"))])
def test_INV21_criterio_regular_es_un_AND(calificacion, asistencia, esperado):
    assert CriterioDeCertificacion.regular().evaluar(calificacion, asistencia) == esperado


def test_INV21_criterio_oficial():
    assert CriterioDeCertificacion.oficial().evaluar(85, 89) == (False, "asistencia")
