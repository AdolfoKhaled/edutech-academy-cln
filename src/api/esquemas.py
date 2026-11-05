"""DTOs de la API (Pydantic). Separan el contrato HTTP del modelo de dominio."""
from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, Field


class Mensaje(BaseModel):
    mensaje: str = Field(examples=["No existe EDU-O999 en solicitudes"])


class EstudianteOut(BaseModel):
    estudianteId: str
    nombre: str
    preferente: bool
    activo: bool
    ciudad: str


class CursoOut(BaseModel):
    cursoId: str
    nombre: str
    modalidad: str
    precio: Decimal
    habilitado: bool
    grupoId: str
    cupo: int
    ocupados: int
    disponibles: int


class LineaOut(BaseModel):
    cursoId: str
    lugares: int
    precio: Decimal
    subtotal: Decimal


class SolicitudOut(BaseModel):
    solicitudId: str
    estudianteId: str
    estado: str
    fechaSolicitud: date
    autorizada: bool
    promocionActiva: bool
    lineas: list[LineaOut]
    lugares: int
    total: Decimal
    folio: str | None
    motivoLiberacion: str | None
    accionesPermitidas: list[str]
    eventos: list[str]


class SolicitudConMensaje(SolicitudOut):
    mensaje: str


class LineaIn(BaseModel):
    cursoId: str = Field(examples=["EDU-P001"])
    lugares: int = Field(ge=1, examples=[1])


class SolicitudIn(BaseModel):
    estudianteId: str = Field(examples=["EDU-C001"])
    cursos: list[LineaIn]
    autorizada: bool = True
    promocionActiva: bool = False
    fecha: date | None = None


class CancelacionIn(BaseModel):
    motivo: str = Field(default="Cancelada por el estudiante", examples=["El estudiante cambió de horario"])


class EvaluacionOut(BaseModel):
    solicitudId: str
    puedeProcesarse: bool
    motivos: list[str]
    beneficioReferencia: bool
    total: Decimal
    reglas: dict[str, str]


class DatosContactoIn(BaseModel):
    estudianteId: str = Field(examples=["EDU-C001"])
    nombre: str = Field(examples=["Alumno 01"])
    correo: str = Field(examples=["alumno01@example.com"])
    telefono: str = Field(examples=["8100000000"])
    ahora: datetime | None = None


class InscripcionOut(BaseModel):
    mensaje: str
    inscripcionId: str | None = None
    estado: str
    monto: Decimal | None = None
    fechaLimitePago: date | None = None


class PagoIn(BaseModel):
    monto: Decimal = Field(gt=0, examples=[Decimal("566.00")])
    fecha: date | None = None


class EstadoDePagoOut(BaseModel):
    estado: str
    saldoPendiente: Decimal
    fechaLimitePago: date


class VencimientoIn(BaseModel):
    ahora: datetime | None = None


class AsistenciaIn(BaseModel):
    sesion: int = Field(ge=1, le=10, examples=[1])
    presente: bool = True
    ahora: datetime | None = None


class EvaluacionIn(BaseModel):
    clave: str = Field(examples=["parcial-1"])
    tipo: str = Field(examples=["parcial"])
    valor: float = Field(examples=[85])


class CierreActaIn(BaseModel):
    hoy: date | None = None


class LineaActaOut(BaseModel):
    inscripcionId: str
    estudiante: str
    calificacionFinal: float
    porcentajeAsistencia: float
    cumple: bool
    motivo: str | None


class ActaOut(BaseModel):
    grupoId: str
    estado: str
    fechaCierre: date | None
    lineas: list[LineaActaOut]


class CertificadoIn(BaseModel):
    grupoId: str
    inscripcionId: str
    hoy: date | None = None


class CertificadoOut(BaseModel):
    folio: str
    titular: str
    curso: str
    fechaConclusion: date
    codigoQr: str
    dentroDePlazo: bool


class VerificacionOut(BaseModel):
    titular: str
    curso: str
    fechaConclusion: date
    vigencia: str
