"""Paso 9: reglas de EduTech Academy probadas en el dominio (sin base de datos).

Cada prueba lleva el ID de la matriz evidencias/matriz_pia_edutech.csv."""
from datetime import date, datetime, timedelta
from decimal import Decimal

import pytest

from src.domain.errores import (
    DatosIncompletos,
    EdicionBloqueada,
    EvaluacionFueraDeRango,
    SinCupo,
    SobrecupoNoPermitido,
)
from src.domain.expediente import ExpedienteAcademico
from src.domain.grupo import Grupo
from src.domain.inscripcion import EstadoInscripcion, Inscripcion
from src.domain.valores import Cupo, Evaluacion, Modalidad, PagoAcreditado
from tests.apoyo import SESIONES

FIN_SESION_1 = SESIONES[0]


def grupo(maximo, sobrecupo=0, ocupados=0):
    g = Grupo("G-1", "C-1", Cupo(maximo, sobrecupo), list(SESIONES))
    for i in range(ocupados):
        g.reservarLugar(f"{i:05d}")
    return g


def inscripcion(monto=4000):
    return Inscripcion.preinscribir("00001", "E-1", "G-1",
                                    {"nombre": "Ana", "correo": "a@example.com", "telefono": "81"},
                                    monto, date(2026, 11, 9))


# ---------- Regla 1 · INV-03 Cupo del grupo ----------
def test_PIA01_reserva_con_lugar_disponible():
    g = grupo(25, ocupados=10)
    evento = g.reservarLugar("00011")
    assert len(g.ocupados) == 11
    assert evento.fechaLimitePago == date(2026, 11, 9)        # 7 días naturales desde el inicio


def test_PIA02_grupo_lleno_rechaza():
    g = grupo(25, ocupados=25)
    with pytest.raises(SinCupo):
        g.reservarLugar("00026")
    assert len(g.ocupados) == 25                               # no se agregó nada


def test_PIA03_ultimo_lugar_y_sobrecupo_limite():
    g = grupo(25, sobrecupo=2, ocupados=26)                    # 25 + 10% (2 lugares) = 27
    g.reservarLugar("00027")                                   # el último lugar sí entra
    assert len(g.ocupados) == 27
    with pytest.raises(SobrecupoNoPermitido):
        Cupo(25, 3)                                            # 3 lugares ya pasan del 10%


def test_cupo_por_modalidad():
    assert (Modalidad.PRESENCIAL.cupoMaximo, Modalidad.EN_LINEA.cupoMaximo) == (25, 40)


# ---------- Regla 2 · INV-06/07 Pago mínimo del 50% para quedar Inscrito ----------
def test_PIA04_pago_total_formaliza_inscripcion():
    i = inscripcion()
    evento = i.registrarPago(PagoAcreditado(4000, date(2026, 10, 25)))
    assert i.estado is EstadoInscripcion.INSCRITO
    assert evento.folio == "INS-00001"
    assert i.saldoPendiente == 0


def test_PIA05_pago_menor_al_50_es_solo_abono():
    i = inscripcion()
    assert i.registrarPago(PagoAcreditado(1999.99, date(2026, 10, 25))) is None
    assert i.estado is EstadoInscripcion.PREINSCRITO
    assert i.saldoPendiente == Decimal("2000.01")


def test_PIA06_exactamente_50_formaliza():
    i = inscripcion()
    i.registrarPago(PagoAcreditado(1000, date(2026, 10, 25)))
    evento = i.registrarPago(PagoAcreditado(1000, date(2026, 10, 26)))   # 2000 de 4000 = 50%
    assert i.estado is EstadoInscripcion.INSCRITO
    assert evento.folio == "INS-00001"


def test_folio_se_genera_una_sola_vez():
    i = inscripcion()
    i.registrarPago(PagoAcreditado(2000, date(2026, 10, 25)))
    assert i.registrarPago(PagoAcreditado(2000, date(2026, 10, 26))) is None   # no crea otro folio
    assert i.folio == "INS-00001"


def test_plazo_vencido_libera_y_prorroga_lo_evita():
    vencida = inscripcion()
    assert vencida.vencerPlazo(date(2026, 11, 10)).inscripcionId == "00001"
    assert vencida.estado is EstadoInscripcion.LIBERADA
    con_prorroga = inscripcion()
    con_prorroga.autorizarProrroga(date(2026, 11, 15))
    assert con_prorroga.vencerPlazo(date(2026, 11, 10)) is None
    assert con_prorroga.estado is EstadoInscripcion.PREINSCRITO


# ---------- Regla 3 · INV-11 El instructor registra asistencia dentro de 48 horas ----------
def test_PIA07_registro_dentro_de_48_horas():
    e = ExpedienteAcademico("00001", "C-1", "G-1")
    e.registrarAsistencia(1, FIN_SESION_1, True, FIN_SESION_1 + timedelta(hours=47))
    assert e.asistencias[1].presente


def test_PIA08_registro_despues_de_48_horas_bloqueado():
    e = ExpedienteAcademico("00001", "C-1", "G-1")
    with pytest.raises(EdicionBloqueada):
        e.registrarAsistencia(1, FIN_SESION_1, True, FIN_SESION_1 + timedelta(hours=48, minutes=1))
    assert e.asistencias == {}


def test_PIA09_exactamente_48_horas_permitido():
    e = ExpedienteAcademico("00001", "C-1", "G-1")
    e.registrarAsistencia(1, FIN_SESION_1, False, FIN_SESION_1 + timedelta(hours=48))
    assert 1 in e.asistencias


# ---------- Regla 4 · INV-14 Evaluación entre 0 y 100 ----------
@pytest.mark.parametrize("valor", [0, 100])
def test_PIA10_limites_de_evaluacion_validos(valor):
    assert Evaluacion("parcial", valor, "inst-1").valor == valor


@pytest.mark.parametrize("valor", [-1, 100.5])
def test_PIA11_evaluacion_fuera_de_rango(valor):
    with pytest.raises(EvaluacionFueraDeRango):
        Evaluacion("parcial", valor, "inst-1")


# ---------- Regla 5 · REG-01 Datos obligatorios de la solicitud ----------
def test_PIA12_solicitud_sin_correo_rechazada():
    with pytest.raises(DatosIncompletos, match="correo"):
        Inscripcion.preinscribir("00001", "E-1", "G-1", {"nombre": "Ana", "correo": "  ", "telefono": "81"},
                                 4000, date(2026, 11, 9))


def test_asistencia_en_linea_60_por_ciento_o_grabacion_72_horas():
    from src.domain.valores import AsistenciaRegistrada as A
    assert A.acreditaEnLinea(60, None)                        # límite inferior de conexión
    assert not A.acreditaEnLinea(59.9, None)
    assert A.acreditaEnLinea(10, 72)                          # límite de la grabación
    assert not A.acreditaEnLinea(10, 72.1)


def test_fecha_de_registro_se_guarda():
    e = ExpedienteAcademico("00001", "C-1", "G-1")
    ahora = datetime(2026, 11, 3, 9, 0)
    e.registrarAsistencia(1, FIN_SESION_1, True, ahora)
    assert e.asistencias[1].registradaEn == ahora
