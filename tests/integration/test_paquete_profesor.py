"""Carga del paquete de datos del profesor y ejecución de casos_prueba.csv y transiciones_prueba.csv.

Los oráculos se calculan aparte, leyendo los CSV crudos, para no comparar el código consigo mismo."""
from decimal import Decimal

import pytest

from src.domain.errores import CursoNoDisponible, SolicitudNoProcesable, TransicionNoPermitida
from src.infrastructure.carga_csv import base_vacia, cargar_datos, leer
from src.sistema import Sistema
from tests.apoyo import DATOS

ACTORES = {a["actor_id"]: a for a in leer(DATOS, "actores.csv")}
CATALOGO = {c["recurso_id"]: c for c in leer(DATOS, "catalogo.csv")}
OPERACIONES = {o["operacion_id"]: o for o in leer(DATOS, "operaciones.csv")}
DETALLE = leer(DATOS, "detalle_operaciones.csv")


def total_esperado(operacion_id: str) -> Decimal:
    return sum((Decimal(CATALOGO[d["recurso_id"]]["precio_mxn"]) * int(d["cantidad"])
                for d in DETALLE if d["operacion_id"] == operacion_id), Decimal("0.00"))


def procesable_esperado(op: dict) -> bool:
    lineas = any(d["operacion_id"] == op["operacion_id"] for d in DETALLE)
    return ACTORES[op["actor_id"]]["activo"] == "1" and lineas and op["autorizado"] == "1"


def beneficio_esperado(op: dict) -> bool:
    return (ACTORES[op["actor_id"]]["es_preferente"] == "1" and total_esperado(op["operacion_id"]) >= 1500
            and op["promocion_activa"] == "0")


def test_carga_completa(sistema_demo):
    assert len(sistema_demo.estudiantes.todos()) == 40
    assert len(sistema_demo.cursos.todos()) == 20
    assert len(sistema_demo.solicitudes.todas()) == 60
    assert all(s.estado.value == "Preinscrito" for s in sistema_demo.solicitudes.todas())   # SOLICITADA
    assert not base_vacia(sistema_demo)


def test_carga_aplica_INV03_al_cupo_del_catalogo():
    s = Sistema({})
    reporte = cargar_datos(s, DATOS)
    mayores = [k for k, c in CATALOGO.items() if int(c["capacidad_o_stock"]) > 40]
    assert [x.split(":")[0] for x in reporte.cuposAjustados] == mayores
    assert all(g.cupo.capacidad <= 40 for g in s.grupos.todos())
    assert reporte.solicitudesSinCursos == ["EDU-O013", "EDU-O039"]
    assert reporte.lineas == len(DETALLE)
    s.cerrar()


@pytest.mark.parametrize("operacion_id", list(OPERACIONES))
def test_totales_con_decimal(sistema_demo, operacion_id):
    assert sistema_demo.solicitudes.obtener(operacion_id).total.monto == total_esperado(operacion_id)


@pytest.mark.parametrize("caso", leer(DATOS, "casos_prueba.csv"), ids=lambda c: c["caso_id"])
def test_casos_prueba_del_paquete(sistema_demo, caso):
    op = OPERACIONES[caso["operacion_id"]]
    ev = sistema_demo.solicitud.evaluar(caso["operacion_id"])
    if caso["tipo_prueba"] == "validar_operacion":
        assert ev.puedeProcesarse is procesable_esperado(op)
    else:
        assert ev.beneficioReferencia is beneficio_esperado(op)


@pytest.mark.parametrize("caso", leer(DATOS, "transiciones_prueba.csv"), ids=lambda c: c["caso_id"])
def test_transiciones_del_paquete(caso):
    s = Sistema({})
    cargar_datos(s, DATOS)
    sid, accion = caso["operacion_id"], caso["accion_sugerida"]
    op = OPERACIONES[sid]
    lineas = [d for d in DETALLE if d["operacion_id"] == sid]
    valida = procesable_esperado(op) and all(CATALOGO[d["recurso_id"]]["habilitado"] == "1" for d in lineas)
    error_al_formalizar = (SolicitudNoProcesable if not procesable_esperado(op) else CursoNoDisponible)

    if accion == "cancelar":
        assert s.solicitud.cancelar(sid).estado.value == "Liberada"
    elif accion == "saltar_estado":
        with pytest.raises(TransicionNoPermitida):
            s.solicitud.concluir(sid)
        assert s.solicitud.obtener(sid).estado.value == "Preinscrito"
    elif not valida:
        with pytest.raises(error_al_formalizar):
            s.solicitud.formalizar(sid)
        assert s.solicitud.obtener(sid).estado.value == "Preinscrito"
    elif accion == "aprobar":
        assert s.solicitud.formalizar(sid).estado.value == "Inscrito"
    elif accion == "completar":
        s.solicitud.formalizar(sid)
        assert s.solicitud.concluir(sid).estado.value == "Concluido"
    else:                                                       # repetir_aprobacion
        s.solicitud.formalizar(sid)
        with pytest.raises(TransicionNoPermitida):
            s.solicitud.formalizar(sid)
        assert [type(e).__name__ for e in s.solicitud.obtener(sid).eventos].count("SolicitudFormalizada") == 1
    s.cerrar()
