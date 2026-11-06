"""Aggregate Solicitud de inscripción: un estudiante pide lugares en uno o varios cursos.

Máquina de estados (estados de EduTech, no los del paquete del profesor):

    Preinscrito --formalizar--> Inscrito --concluir--> Concluido
         \\--cancelar--> Liberada

Equivalencia con el paquete: SOLICITADA = Preinscrito; ACEPTADA e INSCRITA = Inscrito
(en EduTech la inscripción se formaliza en un solo paso, INV-06/07); FINALIZADA = Concluido;
CANCELADA = Liberada (US-06: se libera el lugar).

Cada transición: 1) valida estado y reglas, 2) cambia el estado, 3) registra el Domain Event.
Si la validación falla se lanza la excepción y nada cambia."""
from dataclasses import dataclass, field
from datetime import date
from enum import Enum

from .curso import Curso
from .errores import CursoNoDisponible, DatosInvalidos, SolicitudNoProcesable, TransicionNoPermitida
from .especificaciones import PUEDE_PROCESARSE, CandidatoSolicitud
from .estudiante import Estudiante
from .eventos import SolicitudConcluida, SolicitudFormalizada, SolicitudLiberada, SolicitudRegistrada
from .valores import Dinero

MAX_LUGARES_POR_CURSO = 10


# Cómo se le explica al usuario cada condición de PUEDE_PROCESARSE que no se cumple.
EXPLICACION = {
    "estudiante activo": "el estudiante está dado de baja",
    "solicitud con al menos un curso": "la solicitud no tiene ningún curso",
    "solicitud autorizada": "la solicitud no está autorizada",
}


class EstadoSolicitud(Enum):
    PREINSCRITO = "Preinscrito"
    INSCRITO = "Inscrito"
    CONCLUIDO = "Concluido"
    LIBERADA = "Liberada"


# Transiciones permitidas: acción -> (estado requerido, estado destino)
TRANSICIONES = {
    "formalizar": (EstadoSolicitud.PREINSCRITO, EstadoSolicitud.INSCRITO),
    "concluir": (EstadoSolicitud.INSCRITO, EstadoSolicitud.CONCLUIDO),
    "cancelar": (EstadoSolicitud.PREINSCRITO, EstadoSolicitud.LIBERADA),
}


@dataclass(frozen=True)
class LineaDeSolicitud:
    """Value Object: lugares pedidos en un curso, con el precio vigente al solicitar."""
    cursoId: str
    lugares: int
    precio: Dinero

    def __post_init__(self):
        if not self.cursoId.strip():
            raise DatosInvalidos("La línea necesita un curso")
        if not 0 < self.lugares <= MAX_LUGARES_POR_CURSO:
            raise DatosInvalidos(f"Los lugares por curso van de 1 a {MAX_LUGARES_POR_CURSO}.")

    @property
    def subtotal(self) -> Dinero:
        return self.precio.por(self.lugares)


@dataclass
class SolicitudDeInscripcion:
    solicitudId: str
    estudianteId: str
    fechaSolicitud: date
    promocionActiva: bool = False
    autorizada: bool = False
    referencia: str = ""
    lineas: list[LineaDeSolicitud] = field(default_factory=list)
    estado: EstadoSolicitud = EstadoSolicitud.PREINSCRITO
    folio: str | None = None
    motivoLiberacion: str | None = None
    eventos: list = field(default_factory=list)

    @classmethod
    def registrar(cls, solicitudId: str, estudianteId: str, fecha: date, autorizada: bool = False,
                  promocionActiva: bool = False, referencia: str = "") -> "SolicitudDeInscripcion":
        s = cls(solicitudId, estudianteId, fecha, promocionActiva, autorizada, referencia)
        s.eventos.append(SolicitudRegistrada(solicitudId, estudianteId))
        return s

    @property
    def total(self) -> Dinero:
        total = Dinero.de(0)
        for linea in self.lineas:
            total = total + linea.subtotal
        return total

    @property
    def lugares(self) -> int:
        return sum(linea.lugares for linea in self.lineas)

    @property
    def accionesPermitidas(self) -> list[str]:
        return [accion for accion, (requerido, _) in TRANSICIONES.items() if requerido is self.estado]

    def agregarCurso(self, curso: Curso, lugares: int) -> None:
        self._exigir("agregar cursos a", EstadoSolicitud.PREINSCRITO)
        if any(linea.cursoId == curso.cursoId for linea in self.lineas):
            raise DatosInvalidos(f"El curso {curso.cursoId} ya está en la solicitud; "
                                 "cambia los lugares en vez de repetirlo.")
        self.lineas.append(LineaDeSolicitud(curso.cursoId, lugares, Dinero.de(curso.costo)))

    def formalizar(self, estudiante: Estudiante, cursos: dict[str, Curso]) -> SolicitudFormalizada:
        self._exigir("formalizar", EstadoSolicitud.PREINSCRITO)
        incumplidas = PUEDE_PROCESARSE.incumplidas(CandidatoSolicitud(self, estudiante))
        if incumplidas:
            motivos = "; ".join(EXPLICACION.get(m, m) for m in incumplidas)
            raise SolicitudNoProcesable(f"No se puede formalizar la solicitud {self.solicitudId}: {motivos}.")
        deshabilitados = [c for c in (linea.cursoId for linea in self.lineas) if not cursos[c].habilitado]
        if deshabilitados:
            lista = ", ".join(deshabilitados)
            raise CursoNoDisponible(f"No se puede formalizar la solicitud {self.solicitudId}: el curso {lista} "
                                    "no está disponible en el catálogo.")
        self.estado = EstadoSolicitud.INSCRITO
        self.folio = f"INS-{self.solicitudId}"          # INV-08: el folio se genera una sola vez
        evento = SolicitudFormalizada(self.solicitudId, self.folio, str(self.total.monto))
        self.eventos.append(evento)
        return evento

    def concluir(self) -> SolicitudConcluida:
        self._exigir("concluir", EstadoSolicitud.INSCRITO)
        self.estado = EstadoSolicitud.CONCLUIDO
        evento = SolicitudConcluida(self.solicitudId)
        self.eventos.append(evento)
        return evento

    def cancelar(self, motivo: str = "Cancelada por el estudiante") -> SolicitudLiberada:
        self._exigir("cancelar", EstadoSolicitud.PREINSCRITO)
        if not motivo or not motivo.strip():
            raise DatosInvalidos("Escribe el motivo de la cancelación.")
        self.estado = EstadoSolicitud.LIBERADA
        self.motivoLiberacion = motivo.strip()
        evento = SolicitudLiberada(self.solicitudId, self.motivoLiberacion)
        self.eventos.append(evento)
        return evento

    def _exigir(self, accion: str, requerido: EstadoSolicitud) -> None:
        if self.estado is not requerido:
            raise TransicionNoPermitida(
                f"No se puede {accion} la solicitud {self.solicitudId} porque está en estado {self.estado.value}. "
                f"Solo se puede {accion} cuando está en {requerido.value}.")
