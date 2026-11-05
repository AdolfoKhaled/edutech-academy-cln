"""Composition root: crea la infraestructura y la inyecta en los Application Services.

Es el único lugar que conoce las clases concretas (SQLAlchemy, adapters); los servicios reciben
interfaces (Dependency Inversion)."""
from .application.acta_service import ActaService
from .application.asistencia_service import AsistenciaService
from .application.calificacion_service import CalificacionService
from .application.certificado_service import CertificadoService
from .application.consultas import EstadoDePagoQuery, VerificacionPublicaService
from .application.inscripcion_service import InscripcionService
from .application.solicitud_service import SolicitudService
from .domain.servicios import CalendarioDeDiasHabiles, ConsolidadorDeActa
from .infrastructure.adapters import (
    ControlDeAccesoAdapter,
    LmsAdapter,
    NotificacionGatewayAdapter,
    SistemaContableAdapter,
)
from .infrastructure.sql import (
    BaseDeDatos,
    EstadoDePagoSqlReader,
    SqlActaRepository,
    SqlCertificadoRepository,
    SqlCursoRepository,
    SqlEstudianteRepository,
    SqlExpedienteRepository,
    SqlGrupoRepository,
    SqlInscripcionRepository,
    SqlSolicitudRepository,
    SqlUnitOfWork,
    VerificacionPublicaSqlReader,
)


class Sistema:
    def __init__(self, roles: dict[str, set[str]], database_url: str = "sqlite://", inhabiles=None):
        db = self.db = BaseDeDatos(database_url)
        uow = SqlUnitOfWork(db)
        self.cursos, self.grupos = SqlCursoRepository(db), SqlGrupoRepository(db)
        self.inscripciones, self.expedientes = SqlInscripcionRepository(db), SqlExpedienteRepository(db)
        self.actas, self.certificados = SqlActaRepository(db), SqlCertificadoRepository(db)
        self.estudiantes, self.solicitudes = SqlEstudianteRepository(db), SqlSolicitudRepository(db)
        self.notificaciones = NotificacionGatewayAdapter()
        self.acceso = ControlDeAccesoAdapter({**roles, LmsAdapter.USUARIO: {"LMS"}})
        calendario = CalendarioDeDiasHabiles(inhabiles)
        self.inscripcion = InscripcionService(uow, self.cursos, self.grupos, self.inscripciones,
                                              self.expedientes, self.notificaciones)
        self.asistencia = AsistenciaService(uow, self.expedientes, self.grupos, self.acceso, calendario)
        self.calificacion = CalificacionService(uow, self.expedientes, self.inscripciones, self.cursos)
        self.acta = ActaService(uow, self.actas, self.grupos, self.inscripciones, self.expedientes, self.cursos,
                                ConsolidadorDeActa(), calendario)
        self.certificado = CertificadoService(uow, self.certificados, self.actas, self.acceso, calendario)
        self.solicitud = SolicitudService(uow, self.solicitudes, self.estudiantes, self.cursos, self.grupos)
        self.verificacion = VerificacionPublicaService(VerificacionPublicaSqlReader(db))
        self.estadoDePago = EstadoDePagoQuery(EstadoDePagoSqlReader(db))
        self.contable = SistemaContableAdapter(self.inscripcion)
        self.lms = LmsAdapter(self.asistencia)

    def cerrar(self) -> None:
        self.db.cerrar()
