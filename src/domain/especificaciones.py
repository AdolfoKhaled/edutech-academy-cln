"""Specification Pattern: cada regla del negocio es un objeto que responde sí o no y se combina
con & (AND), | (OR) y ~ (NOT). Las reglas no modifican nada: solo evalúan.

Además de responder, cada Specification sabe decir qué condición no se cumplió (incumplidas),
para que el rechazo llegue al usuario con un motivo concreto."""
from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal


class Specification:
    nombre = "regla"

    def es_satisfecha_por(self, candidato) -> bool:
        raise NotImplementedError

    def incumplidas(self, candidato) -> list[str]:
        return [] if self.es_satisfecha_por(candidato) else [self.nombre]

    def __and__(self, otra: Specification) -> Specification:
        return Conjuncion(self, otra)

    def __or__(self, otra: Specification) -> Specification:
        return Disyuncion(self, otra)

    def __invert__(self) -> Specification:
        return Negacion(self)


class Conjuncion(Specification):
    """A & B: se cumplen las dos."""
    def __init__(self, izquierda: Specification, derecha: Specification):
        self.izquierda, self.derecha = izquierda, derecha
        self.nombre = f"({izquierda.nombre} Y {derecha.nombre})"

    def es_satisfecha_por(self, candidato) -> bool:
        return self.izquierda.es_satisfecha_por(candidato) and self.derecha.es_satisfecha_por(candidato)

    def incumplidas(self, candidato) -> list[str]:
        return self.izquierda.incumplidas(candidato) + self.derecha.incumplidas(candidato)


class Disyuncion(Specification):
    """A | B: se cumple al menos una."""
    def __init__(self, izquierda: Specification, derecha: Specification):
        self.izquierda, self.derecha = izquierda, derecha
        self.nombre = f"({izquierda.nombre} O {derecha.nombre})"

    def es_satisfecha_por(self, candidato) -> bool:
        return self.izquierda.es_satisfecha_por(candidato) or self.derecha.es_satisfecha_por(candidato)


class Negacion(Specification):
    """~A: no se cumple A."""
    def __init__(self, regla: Specification):
        self.regla = regla
        self.nombre = f"NO {regla.nombre}"

    def es_satisfecha_por(self, candidato) -> bool:
        return not self.regla.es_satisfecha_por(candidato)


# ---------- Reglas sobre una Solicitud de inscripción (paquete de datos del PIA) ----------
@dataclass(frozen=True)
class CandidatoSolicitud:
    """Lo que necesitan las reglas para evaluar una solicitud: la solicitud y su estudiante."""
    solicitud: object        # SolicitudDeInscripcion
    estudiante: object       # Estudiante


class EstudianteActivo(Specification):
    nombre = "estudiante activo"

    def es_satisfecha_por(self, c: CandidatoSolicitud) -> bool:
        return c.estudiante.activo


class TieneLineas(Specification):
    nombre = "solicitud con al menos un curso"

    def es_satisfecha_por(self, c: CandidatoSolicitud) -> bool:
        return len(c.solicitud.lineas) > 0


class Autorizada(Specification):
    nombre = "solicitud autorizada"

    def es_satisfecha_por(self, c: CandidatoSolicitud) -> bool:
        return c.solicitud.autorizada


class EstudiantePreferente(Specification):
    nombre = "estudiante preferente"

    def es_satisfecha_por(self, c: CandidatoSolicitud) -> bool:
        return c.estudiante.preferente


class TotalMinimo(Specification):
    def __init__(self, minimo: Decimal):
        self.minimo = minimo
        self.nombre = f"total >= {minimo} MXN"

    def es_satisfecha_por(self, c: CandidatoSolicitud) -> bool:
        return c.solicitud.total.monto >= self.minimo


class PromocionActiva(Specification):
    nombre = "promoción activa"

    def es_satisfecha_por(self, c: CandidatoSolicitud) -> bool:
        return c.solicitud.promocionActiva


# Regla del paquete: la solicitud puede procesarse (formalizarse).
PUEDE_PROCESARSE = EstudianteActivo() & TieneLineas() & Autorizada()
# Regla del paquete: elegible para el beneficio por referencia.
BENEFICIO_REFERENCIA = EstudiantePreferente() & TotalMinimo(Decimal("1500")) & ~PromocionActiva()


# ---------- Reglas propias de EduTech (BRD) ----------
@dataclass(frozen=True)
class Desempeno:
    calificacion: float
    asistencia: float


class CalificacionMinima(Specification):
    def __init__(self, minimo: float):
        self.minimo = minimo
        self.nombre = "calificación"

    def es_satisfecha_por(self, d: Desempeno) -> bool:
        return d.calificacion >= self.minimo


class AsistenciaMinima(Specification):
    def __init__(self, minimo: float):
        self.minimo = minimo
        self.nombre = "asistencia"

    def es_satisfecha_por(self, d: Desempeno) -> bool:
        return d.asistencia >= self.minimo


@dataclass(frozen=True)
class ConexionEnLinea:
    porcentajeConexion: float
    horasHastaVerGrabacion: float | None


class ConexionMinima(Specification):
    """INV-12: 60 % de conexión a la sesión en vivo."""
    nombre = "60 % de conexión en vivo"

    def es_satisfecha_por(self, c: ConexionEnLinea) -> bool:
        return c.porcentajeConexion >= 60


class GrabacionVistaATiempo(Specification):
    """INV-12: la grabación se vio dentro de las 72 horas siguientes."""
    nombre = "grabación vista en 72 horas"

    def es_satisfecha_por(self, c: ConexionEnLinea) -> bool:
        return c.horasHastaVerGrabacion is not None and c.horasHastaVerGrabacion <= 72


# INV-12: la asistencia en línea se acredita con cualquiera de las dos condiciones (OR).
ASISTENCIA_EN_LINEA = ConexionMinima() | GrabacionVistaATiempo()
