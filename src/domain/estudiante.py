"""Entity Estudiante: la persona que se inscribe (actor "alumno" del paquete de datos)."""
from dataclasses import dataclass


@dataclass
class Estudiante:
    estudianteId: str
    nombre: str
    preferente: bool = False      # es_preferente del paquete; habilita el beneficio por referencia
    activo: bool = True           # un estudiante dado de baja no puede formalizar solicitudes
    ciudad: str = ""
