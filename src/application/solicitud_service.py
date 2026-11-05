"""Solicitudes de inscripción a uno o varios cursos (paquete de datos del PIA, US-04 y US-06)."""
from dataclasses import dataclass
from datetime import date

from ..domain.especificaciones import BENEFICIO_REFERENCIA, PUEDE_PROCESARSE, CandidatoSolicitud
from ..domain.repositorios import CursoRepository, EstudianteRepository, GrupoRepository, SolicitudRepository
from ..domain.solicitud import SolicitudDeInscripcion
from .puertos import UnitOfWork, transaccion


def grupoDelCurso(cursoId: str) -> str:
    """Cada curso del catálogo tiene un grupo abierto con el mismo código (G-<curso>)."""
    return f"G-{cursoId}"


@dataclass(frozen=True)
class RegistrarSolicitud:
    """Command: el estudiante pide lugares en uno o varios cursos."""
    estudianteId: str
    cursos: list[tuple[str, int]]          # (cursoId, lugares)
    fecha: date
    autorizada: bool = True
    promocionActiva: bool = False
    referencia: str = ""


@dataclass(frozen=True)
class EvaluacionDeSolicitud:
    """Resultado de las Specifications sobre una solicitud, sin modificarla."""
    solicitudId: str
    puedeProcesarse: bool
    motivos: list[str]
    beneficioReferencia: bool
    total: str


class SolicitudService:
    def __init__(self, uow: UnitOfWork, solicitudes: SolicitudRepository, estudiantes: EstudianteRepository,
                 cursos: CursoRepository, grupos: GrupoRepository):
        self.uow, self.solicitudes, self.estudiantes = uow, solicitudes, estudiantes
        self.cursos, self.grupos = cursos, grupos

    def registrar(self, cmd: RegistrarSolicitud) -> SolicitudDeInscripcion:
        with transaccion(self.uow):
            self.estudiantes.obtener(cmd.estudianteId)                       # 404 si no existe
            solicitud = SolicitudDeInscripcion.registrar(self.solicitudes.siguienteId(), cmd.estudianteId,
                                                         cmd.fecha, cmd.autorizada, cmd.promocionActiva,
                                                         cmd.referencia)
            for cursoId, lugares in cmd.cursos:
                solicitud.agregarCurso(self.cursos.obtener(cursoId), lugares)
            self.solicitudes.guardar(solicitud)
        return solicitud

    def obtener(self, solicitudId: str) -> SolicitudDeInscripcion:
        return self.solicitudes.obtener(solicitudId)

    def listar(self, estado: str | None = None) -> list[SolicitudDeInscripcion]:
        todas = self.solicitudes.todas()
        return [s for s in todas if estado is None or s.estado.value.lower() == estado.lower()]

    def evaluar(self, solicitudId: str) -> EvaluacionDeSolicitud:
        solicitud = self.solicitudes.obtener(solicitudId)
        candidato = CandidatoSolicitud(solicitud, self.estudiantes.obtener(solicitud.estudianteId))
        motivos = PUEDE_PROCESARSE.incumplidas(candidato)
        return EvaluacionDeSolicitud(solicitudId, not motivos, motivos,
                                     BENEFICIO_REFERENCIA.es_satisfecha_por(candidato), str(solicitud.total.monto))

    def formalizar(self, solicitudId: str) -> SolicitudDeInscripcion:
        """Preinscrito → Inscrito: valida las reglas y reserva los lugares en los grupos (INV-03)."""
        with transaccion(self.uow):
            solicitud = self.solicitudes.obtener(solicitudId)
            estudiante = self.estudiantes.obtener(solicitud.estudianteId)
            cursos = {linea.cursoId: self.cursos.obtener(linea.cursoId) for linea in solicitud.lineas}
            solicitud.formalizar(estudiante, cursos)
            for linea in solicitud.lineas:
                grupo = self.grupos.obtener(grupoDelCurso(linea.cursoId))
                for n in range(1, linea.lugares + 1):
                    grupo.reservarLugar(f"{solicitudId}-{linea.cursoId}-{n}")   # SinCupo revierte todo
                self.grupos.guardar(grupo)
            self.solicitudes.guardar(solicitud)
        return solicitud

    def concluir(self, solicitudId: str) -> SolicitudDeInscripcion:
        with transaccion(self.uow):
            solicitud = self.solicitudes.obtener(solicitudId)
            solicitud.concluir()
            self.solicitudes.guardar(solicitud)
        return solicitud

    def cancelar(self, solicitudId: str, motivo: str = "Cancelada por el estudiante") -> SolicitudDeInscripcion:
        with transaccion(self.uow):
            solicitud = self.solicitudes.obtener(solicitudId)
            solicitud.cancelar(motivo)
            self.solicitudes.guardar(solicitud)
        return solicitud
