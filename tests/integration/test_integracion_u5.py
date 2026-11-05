"""Persistencia (SQLAlchemy), servicio externo simulado con Mock y autorización (Unidad 5)."""
from datetime import date, datetime, timedelta
from unittest.mock import Mock

import pytest
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError

from src.application.inscripcion_service import EnListaDeEspera, SolicitarInscripcion, SolicitudRegistrada
from src.application.puertos import AccesoDenegado, NotificacionGateway
from src.domain.errores import CertificadoNoAutorizado, DatosIncompletos, NoEncontrado
from src.infrastructure.sql import (
    BaseDeDatos,
    SqlGrupoRepository,
    SqlInscripcionRepository,
    SqlUnitOfWork,
    certificados,
    cursos,
    inscripciones,
)
from tests.apoyo import ANTES, SESIONES, crear_sistema, datos


def solicitar(s, estudiante="E-1", nombre="Ana López", ahora=ANTES):
    return s.inscripcion.solicitarInscripcion(SolicitarInscripcion(estudiante, "G-1", datos(nombre), ahora))


# ---------- Persistencia y transacciones ----------
def test_PIA13_commit_la_solicitud_queda_guardada(sistema):
    r = solicitar(sistema)
    # Se lee con repositorios nuevos sobre la misma base: lo que quedó es lo confirmado (COMMIT).
    otra_lectura = SqlInscripcionRepository(sistema.db).obtener(r.inscripcionId)
    assert isinstance(r, SolicitudRegistrada)
    assert otra_lectura.estado.value == "Preinscrito"
    assert SqlGrupoRepository(sistema.db).obtener("G-1").ocupados == [r.inscripcionId]
    assert sistema.estadoDePago.consultarEstadoDePago(r.inscripcionId).saldoPendiente == 4000


def test_PIA14_rollback_datos_incompletos_no_guardan_nada(sistema):
    with pytest.raises(DatosIncompletos):
        sistema.inscripcion.solicitarInscripcion(SolicitarInscripcion("E-1", "G-1", {"nombre": "Ana"}, ANTES))
    # El Grupo ya había reservado el lugar en memoria; el ROLLBACK lo descarta.
    assert sistema.grupos.obtener("G-1").ocupados == []
    assert sistema.db.ejecutar(select(func.count()).select_from(inscripciones))[0][0] == 0


def test_PIA15_unidad_de_trabajo_rollback_directo():
    db = BaseDeDatos("sqlite://")
    uow = SqlUnitOfWork(db)
    uow.iniciar()
    db.ejecutar(cursos.insert().values(id="C-9", datos=b"0"))
    uow.cancelar()
    assert db.ejecutar(select(func.count()).select_from(cursos))[0][0] == 0


def test_PIA16_restriccion_unica_un_certificado_por_inscripcion():
    db = BaseDeDatos("sqlite://")
    db.ejecutar(certificados.insert().values(folio="CERT-1", inscripcion="00001", datos=b"0"))
    with pytest.raises(IntegrityError):
        db.ejecutar(certificados.insert().values(folio="CERT-2", inscripcion="00001", datos=b"0"))


def test_registro_inexistente_lanza_no_encontrado(sistema):
    with pytest.raises(NoEncontrado):
        sistema.inscripciones.obtener("99999")
    with pytest.raises(NoEncontrado):
        sistema.estadoDePago.consultarEstadoDePago("99999")


# ---------- Servicio externo simulado: aviso de lugar disponible ----------
def test_PIA17_mock_avisa_al_siguiente_en_lista_de_espera():
    s = crear_sistema(maximo=1)
    aviso = Mock(spec=NotificacionGateway)                  # no se envía ningún correo real
    s.inscripcion.notificaciones = aviso
    primera = solicitar(s)                                  # ocupa el único lugar
    assert isinstance(solicitar(s, "E-2", "Luis"), EnListaDeEspera)
    hoy = datetime(2026, 11, 10, 9, 0)                      # un día después del límite de pago
    eventos = s.inscripcion.liberarPorPlazoVencido(primera.inscripcionId, hoy)
    assert [type(e).__name__ for e in eventos] == ["PlazoDePagoVencido", "LugarLiberado",
                                                   "LugarOfrecidoAlSiguienteEnEspera"]
    aviso.notificarLugarDisponible.assert_called_once_with("E-2", hoy + timedelta(hours=24))


def test_PIA18_mock_sin_vencimiento_no_avisa():
    s = crear_sistema(maximo=1)
    aviso = Mock(spec=NotificacionGateway)
    s.inscripcion.notificaciones = aviso
    primera = solicitar(s)
    solicitar(s, "E-2", "Luis")
    assert s.inscripcion.liberarPorPlazoVencido(primera.inscripcionId, datetime(2026, 11, 9, 9, 0)) == []
    aviso.notificarLugarDisponible.assert_not_called()      # el día límite todavía no vence


def test_mock_falla_del_servicio_externo_despues_del_commit():
    """Si el envío del aviso falla, la liberación ya quedó guardada (se notifica después del COMMIT)."""
    s = crear_sistema(maximo=1)
    aviso = Mock(spec=NotificacionGateway)
    aviso.notificarLugarDisponible.side_effect = TimeoutError("servicio de correo sin respuesta")
    s.inscripcion.notificaciones = aviso
    primera = solicitar(s)
    solicitar(s, "E-2", "Luis")
    with pytest.raises(TimeoutError):
        s.inscripcion.liberarPorPlazoVencido(primera.inscripcionId, datetime(2026, 11, 10, 9, 0))
    assert s.inscripciones.obtener(primera.inscripcionId).estado.value == "Liberada"


def test_pago_notificado_por_sistema_contable(sistema):
    r = solicitar(sistema)
    evento = sistema.contable.pagoNotificado(r.inscripcionId, 2000, date(2026, 10, 25))
    assert evento.folio == f"INS-{r.inscripcionId}"
    assert sistema.estadoDePago.consultarEstadoDePago(r.inscripcionId).estado == "Inscrito"


# ---------- Seguridad: autorización por rol ----------
def test_PIA19_instructor_registra_asistencia(sistema):
    r = solicitar(sistema)
    porcentaje = sistema.asistencia.registrarAsistencia(r.inscripcionId, 1, True, "inst-1",
                                                        SESIONES[0] + timedelta(hours=1))
    assert porcentaje == 10.0                               # 1 de 10 sesiones


def test_PIA20_control_escolar_no_registra_como_instructor(sistema):
    r = solicitar(sistema)
    with pytest.raises(AccesoDenegado):
        sistema.asistencia.registrarAsistencia(r.inscripcionId, 1, True, "ce-1", SESIONES[0])


def test_PIA21_solo_coordinacion_emite_certificado(sistema):
    with pytest.raises(CertificadoNoAutorizado):
        sistema.certificado.emitirCertificado("G-1", "00001", "inst-1", date(2026, 11, 20))


def test_usuario_desconocido_sin_permisos(sistema):
    r = solicitar(sistema)
    with pytest.raises(AccesoDenegado):
        sistema.asistencia.registrarAsistencia(r.inscripcionId, 1, True, "intruso", SESIONES[0])
