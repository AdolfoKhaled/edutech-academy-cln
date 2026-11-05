"""API REST de punta a punta con TestClient: códigos HTTP del contrato y casos de uso CU-01 a CU-05."""
from datetime import datetime, timedelta

import pytest
from fastapi.testclient import TestClient

from src.api.main import crear_app
from src.config import Configuracion
from src.infrastructure.carga_csv import SESIONES_DEMO
from tests.apoyo import DATOS, ROLES

INSTRUCTOR, CONTROL, COORD = ({"X-Usuario": u} for u in ("inst-1", "ce-1", "coord-1"))


@pytest.fixture
def api():
    app = crear_app(Configuracion(database_url="sqlite://", datos_dir=DATOS, roles=ROLES))
    with TestClient(app) as cliente:
        yield cliente


# ---------- General y documentación ----------
def test_salud_y_swagger(api):
    r = api.get("/salud")
    assert r.status_code == 200 and r.json()["solicitudes"] == 60 and r.json()["baseDeDatos"] == "sqlite"
    assert api.get("/docs").status_code == 200
    assert api.get("/", follow_redirects=False).headers["location"] == "/docs"
    rutas = api.get("/openapi.json").json()["paths"]
    assert {"/solicitudes/{solicitudId}/formalizar", "/certificados", "/verificacion/{folio}"} <= set(rutas)


def test_catalogo(api):
    assert len(api.get("/estudiantes").json()) == 40
    assert api.get("/estudiantes/EDU-C007").json()["activo"] is False
    cursos = api.get("/cursos").json()
    assert len(cursos) == 20 and max(c["cupo"] for c in cursos) == 40       # INV-03 aplicado
    assert api.get("/cursos/EDU-P011").json()["habilitado"] is False


# ---------- Solicitudes: códigos 200, 201, 400, 404, 409, 422 ----------
def test_flujo_de_solicitud(api):
    r = api.post("/solicitudes/EDU-O001/formalizar")
    assert r.status_code == 200
    assert r.json()["estado"] == "Inscrito" and r.json()["folio"] == "INS-EDU-O001"
    assert api.get("/cursos/EDU-P014").json()["ocupados"] == 4
    r = api.post("/solicitudes/EDU-O001/concluir")
    assert r.json()["estado"] == "Concluido"
    assert r.json()["eventos"] == ["SolicitudRegistrada", "SolicitudFormalizada", "SolicitudConcluida"]


def test_409_transicion_no_permitida(api):
    api.post("/solicitudes/EDU-O003/formalizar")
    r = api.post("/solicitudes/EDU-O003/formalizar")
    assert r.status_code == 409
    assert r.json() == {"mensaje": "No se puede formalizar una solicitud en estado Inscrito; se requiere Preinscrito"}
    assert api.post("/solicitudes/EDU-O004/concluir").status_code == 409


def test_422_regla_de_negocio(api):
    r = api.post("/solicitudes/EDU-O013/formalizar")              # sin cursos
    assert r.status_code == 422 and "al menos un curso" in r.json()["mensaje"]
    assert api.post("/solicitudes/EDU-O005/formalizar").status_code == 422   # curso deshabilitado


def test_404_no_existe(api):
    assert api.get("/solicitudes/EDU-O999").json() == {"mensaje": "No existe EDU-O999 en solicitudes"}
    assert api.post("/solicitudes/EDU-O999/formalizar").status_code == 404
    assert api.get("/cursos/NADA").status_code == 404


def test_cancelar_con_y_sin_motivo(api):
    r = api.post("/solicitudes/EDU-O002/cancelar", json={"motivo": "Cambio de horario"})
    assert r.json()["estado"] == "Liberada" and r.json()["motivoLiberacion"] == "Cambio de horario"
    assert api.post("/solicitudes/EDU-O007/cancelar").json()["motivoLiberacion"] == "Cancelada por el estudiante"
    assert len(api.get("/solicitudes", params={"estado": "Liberada"}).json()) == 2


def test_evaluacion_de_specifications(api):
    r = api.get("/solicitudes/EDU-O001/evaluacion").json()
    assert r["puedeProcesarse"] is True and r["total"] == "9358.00"
    assert "NO promoción activa" in r["reglas"]["beneficioReferencia"]


def test_201_registrar_y_400_mal_formada(api):
    r = api.post("/solicitudes", json={"estudianteId": "EDU-C001", "cursos": [{"cursoId": "EDU-P001", "lugares": 2}],
                                       "fecha": "2026-11-05"})
    assert r.status_code == 201 and r.json()["total"] == "1132.00" and r.json()["estado"] == "Preinscrito"
    r = api.post("/solicitudes", json={"cursos": []})
    assert r.status_code == 400 and r.json() == {"mensaje": "Falta el dato 'estudianteId' en la petición."}
    r = api.post("/solicitudes", json={"estudianteId": "EDU-C001", "cursos": [{"cursoId": "EDU-P001", "lugares": 0}]})
    assert r.status_code == 400 and "lugares" in r.json()["mensaje"]
    r = api.post("/solicitudes", json={"estudianteId": "EDU-C001", "cursos": [{"cursoId": "EDU-P001", "lugares": 11}]})
    assert r.status_code == 422


def test_reiniciar_demo(api):
    api.post("/solicitudes/EDU-O001/formalizar")
    r = api.post("/demo/reiniciar")
    assert r.status_code == 200 and r.json()["solicitudes"] == 60 and len(r.json()["cuposAjustadosINV03"]) == 4
    assert api.get("/solicitudes/EDU-O001").json()["estado"] == "Preinscrito"


# ---------- CU-01 a CU-05 por la API, con fechas controladas ----------
def inscribir(api, estudiante, nombre, grupo="G-EDU-P001"):
    return api.post(f"/grupos/{grupo}/inscripciones", json={
        "estudianteId": estudiante, "nombre": nombre, "correo": "alumno@example.com", "telefono": "8100000000",
        "ahora": "2026-11-01T10:00:00"})


def test_curso_completo_por_la_api(api):
    r = inscribir(api, "EDU-C001", "Alumno 01")
    assert r.status_code == 201 and r.json()["estado"] == "Preinscrito"
    iid = r.json()["inscripcionId"]
    assert api.get(f"/inscripciones/{iid}/estado-de-pago").json()["saldoPendiente"] == "566.00"
    r = api.post(f"/inscripciones/{iid}/pagos", json={"monto": "283.00", "fecha": "2026-11-02"})
    assert r.json()["estado"] == "Inscrito" and "INS-" in r.json()["mensaje"]          # 50 % formaliza

    for n, fin in enumerate(SESIONES_DEMO, start=1):                                     # CU-02
        r = api.post(f"/inscripciones/{iid}/asistencias", headers=INSTRUCTOR,
                     json={"sesion": n, "ahora": (fin + timedelta(hours=1)).isoformat()})
    assert r.json()["porcentajeAsistencia"] == 100.0
    for clave, tipo, valor in (("p1", "parcial", 80), ("pf", "proyecto", 90), ("a1", "actividad", 70)):  # CU-03
        r = api.post(f"/inscripciones/{iid}/evaluaciones", headers=INSTRUCTOR,
                     json={"clave": clave, "tipo": tipo, "valor": valor})
    assert r.json()["calificacionFinal"] == 82.0

    assert api.post("/grupos/G-EDU-P001/acta/cierre", json={"hoy": "2026-11-28"}).status_code == 422   # INV-18
    r = api.post("/grupos/G-EDU-P001/acta/cierre", json={"hoy": "2026-12-04"})                     # CU-04
    assert r.json()["estado"] == "Cerrada" and r.json()["lineas"][0]["cumple"] is True
    assert api.post("/grupos/G-EDU-P001/acta/cierre", json={"hoy": "2026-12-05"}).status_code == 409   # INV-22

    cert = {"grupoId": "G-EDU-P001", "inscripcionId": iid, "hoy": "2026-12-07"}
    assert api.post("/certificados", json=cert, headers=INSTRUCTOR).status_code == 403                # INV-24
    r = api.post("/certificados", json=cert, headers=COORD)                                           # CU-05
    assert r.status_code == 201 and r.json()["folio"] == f"CERT-{iid}"
    assert api.post("/certificados", json=cert, headers=COORD).status_code == 409                     # INV-25
    r = api.get(f"/verificacion/CERT-{iid}")
    assert r.json() == {"titular": "Alumno 01", "curso": "Cloud 01", "fechaConclusion": "2026-11-27",
                        "vigencia": "Vigente"}
    assert api.get("/verificacion/CERT-NADA").status_code == 404


def test_permisos_y_ventana_de_48_horas(api):
    iid = inscribir(api, "EDU-C001", "Alumno 01").json()["inscripcionId"]
    fin = SESIONES_DEMO[0]
    r = api.post(f"/inscripciones/{iid}/asistencias", headers=CONTROL, json={"sesion": 1})
    assert r.status_code == 403
    r = api.post(f"/inscripciones/{iid}/asistencias", json={"sesion": 1})
    assert r.status_code == 400 and "X-Usuario" in r.json()["mensaje"]
    tarde = (fin + timedelta(hours=49)).isoformat()
    r = api.post(f"/inscripciones/{iid}/asistencias", headers=INSTRUCTOR, json={"sesion": 1, "ahora": tarde})
    assert r.status_code == 409                                                                       # INV-11
    r = api.post(f"/inscripciones/{iid}/evaluaciones", headers=INSTRUCTOR,
                 json={"clave": "p1", "tipo": "parcial", "valor": 80})
    assert r.status_code == 422                                                                       # INV-16
    api.post(f"/inscripciones/{iid}/pagos", json={"monto": "566.00"})
    api.post(f"/inscripciones/{iid}/evaluaciones", headers=INSTRUCTOR,
             json={"clave": "p1", "tipo": "parcial", "valor": 80})
    r = api.post(f"/inscripciones/{iid}/evaluaciones", headers={"X-Usuario": "inst-2"},
                 json={"clave": "p1", "tipo": "parcial", "valor": 95})
    assert r.status_code == 403                                                                       # INV-17


def test_lista_de_espera_y_vencimiento(api):
    api.post("/demo/reiniciar")
    grupo = "G-EDU-P001"           # cupo 13
    ids = [inscribir(api, f"EDU-C{n:03d}", f"Alumno {n:02d}", grupo).json()["inscripcionId"] for n in range(1, 14)]
    r = inscribir(api, "EDU-C020", "Alumno 20", grupo)
    assert r.status_code == 202 and r.json()["estado"] == "En lista de espera"
    r = api.post(f"/inscripciones/{ids[0]}/vencimiento", json={"ahora": "2026-11-23T09:00:00"})
    assert r.json()["eventos"] == []                                                # el día límite sigue vigente
    r = api.post(f"/inscripciones/{ids[0]}/vencimiento", json={"ahora": "2026-11-24T09:00:00"})
    assert r.json()["eventos"] == ["PlazoDePagoVencido", "LugarLiberado", "LugarOfrecidoAlSiguienteEnEspera"]


def test_peticion_con_tipo_invalido(api):
    r = api.post("/inscripciones/00001/pagos", json={"monto": "abc"})
    assert r.status_code == 400 and r.json()["mensaje"].startswith("El dato 'monto' no es válido")


def test_inicio_perezoso_con_base_de_archivo(tmp_path):
    url = f"sqlite:///{tmp_path / 'demo.db'}"
    cfg = Configuracion(database_url=url, datos_dir=DATOS, roles=ROLES)
    with TestClient(crear_app(cfg)) as c:
        c.post("/solicitudes/EDU-O001/formalizar")
    with TestClient(crear_app(cfg)) as c:                     # la base persiste y no se vuelve a cargar
        assert c.get("/solicitudes/EDU-O001").json()["estado"] == "Inscrito"


def test_fecha_actual_por_defecto(api):
    iid = inscribir(api, "EDU-C001", "Alumno 01").json()["inscripcionId"]
    r = api.post(f"/inscripciones/{iid}/vencimiento")
    assert r.status_code == 200
    assert datetime.now().year >= 2026
