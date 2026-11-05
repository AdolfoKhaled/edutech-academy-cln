import warnings

import pytest

from tests.apoyo import DATOS, sistemaConGrupo

warnings.filterwarnings("ignore", category=ResourceWarning)


@pytest.fixture
def sistema():
    s = sistemaConGrupo()
    yield s
    s.cerrar()


@pytest.fixture
def sistema_demo():
    """Sistema con el paquete de datos del profesor cargado (40 estudiantes, 20 cursos, 60 solicitudes)."""
    from src.infrastructure.carga_csv import cargar_datos
    from src.sistema import Sistema
    s = Sistema({})
    cargar_datos(s, DATOS)
    yield s
    s.cerrar()
