"""CU-04 Identificación de criterios de certificación (cierre de acta)."""
from datetime import date

from ..domain.acta import Acta
from ..domain.errores import NoEncontrado
from ..domain.inscripcion import EstadoInscripcion
from ..domain.repositorios import (
    ActaRepository,
    CursoRepository,
    ExpedienteRepository,
    GrupoRepository,
    InscripcionRepository,
)
from ..domain.servicios import CalendarioDeDiasHabiles, ConsolidadorDeActa
from .puertos import UnitOfWork, transaccion


class ActaService:
    def __init__(self, uow: UnitOfWork, actas: ActaRepository, grupos: GrupoRepository,
                 inscripciones: InscripcionRepository, expedientes: ExpedienteRepository, cursos: CursoRepository,
                 consolidador: ConsolidadorDeActa, calendario: CalendarioDeDiasHabiles):
        self.uow, self.actas, self.grupos, self.inscripciones = uow, actas, grupos, inscripciones
        self.expedientes, self.cursos = expedientes, cursos
        self.consolidador, self.calendario = consolidador, calendario

    def cerrarActa(self, grupoId: str, hoy: date) -> Acta:
        with transaccion(self.uow):
            grupo = self.grupos.obtener(grupoId)
            curso = self.cursos.obtener(grupo.cursoId)
            try:
                acta = self.actas.obtener(grupoId)
            except NoEncontrado:
                acta = Acta(grupoId, curso.nombre)
            # INV-20: solo las inscripciones en estado Inscrito figuran en el acta.
            inscritas = [i for i in self.inscripciones.delGrupo(grupoId) if i.estado is EstadoInscripcion.INSCRITO]
            expedientes = [(self.expedientes.obtener(i.inscripcionId), i.datos["nombre"]) for i in inscritas]
            lineas, sinAsistencia = self.consolidador.consolidar(expedientes, curso.criterio, curso.ponderacion,
                                                                 len(grupo.sesiones))
            permitida = self.calendario.sumarDiasHabiles(grupo.ultimaSesion, 5)      # INV-18
            acta.cerrar(lineas, sinAsistencia, hoy, permitida, grupo.ultimaSesion)   # INV-19, INV-22
            self.actas.guardar(acta)
            for expediente, _ in expedientes:      # reacción a ActaCerrada: ya no aceptan cambios
                expediente.cerrar()
                self.expedientes.guardar(expediente)
        return acta
