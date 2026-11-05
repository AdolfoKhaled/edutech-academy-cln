"""API REST de EduTech Academy (FastAPI). Solo traduce HTTP a casos de uso: las reglas viven en el
dominio y los servicios de aplicación. Documentación interactiva en /docs (Swagger UI) y /openapi.json.

Contrato de respuestas:
  200/201 éxito · 202 en lista de espera · 400 petición mal formada · 403 sin permiso
  404 no existe · 409 la máquina de estados o el momento no lo permiten · 422 regla de negocio incumplida"""
import threading
from datetime import date, datetime
from typing import Annotated

from fastapi import FastAPI, Header, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse, RedirectResponse
from sqlalchemy.exc import IntegrityError

from ..application.inscripcion_service import EnListaDeEspera, SolicitarInscripcion
from ..application.puertos import AccesoDenegado
from ..application.solicitud_service import RegistrarSolicitud, grupoDelCurso
from ..config import Configuracion
from ..domain.errores import (
    ActaYaCerrada,
    CertificadoNoAutorizado,
    EdicionBloqueada,
    ErrorDeDominio,
    EvaluacionDeOtroInstructor,
    NoEncontrado,
    TransicionNoPermitida,
)
from ..domain.especificaciones import BENEFICIO_REFERENCIA, PUEDE_PROCESARSE
from ..infrastructure.carga_csv import base_vacia, cargar_datos
from ..sistema import Sistema
from . import esquemas as E

ESTADO_HTTP = [(NoEncontrado, 404), (AccesoDenegado, 403), (CertificadoNoAutorizado, 403),
               (EvaluacionDeOtroInstructor, 403), (TransicionNoPermitida, 409), (ActaYaCerrada, 409),
               (EdicionBloqueada, 409), (ErrorDeDominio, 422)]
ERRORES = {c: {"model": E.Mensaje} for c in (400, 403, 404, 409, 422)}
Usuario = Annotated[str, Header(alias="X-Usuario", description="Usuario que realiza la acción (rol)",
                                examples=["inst-1"])]


def solicitud_dto(s) -> dict:
    return {"solicitudId": s.solicitudId, "estudianteId": s.estudianteId, "estado": s.estado.value,
            "fechaSolicitud": s.fechaSolicitud, "autorizada": s.autorizada, "promocionActiva": s.promocionActiva,
            "lineas": [{"cursoId": linea.cursoId, "lugares": linea.lugares, "precio": linea.precio.monto,
                        "subtotal": linea.subtotal.monto} for linea in s.lineas],
            "lugares": s.lugares, "total": s.total.monto, "folio": s.folio,
            "motivoLiberacion": s.motivoLiberacion, "accionesPermitidas": s.accionesPermitidas,
            "eventos": [type(e).__name__ for e in s.eventos]}


def crear_app(config: Configuracion | None = None, sistema: Sistema | None = None) -> FastAPI:
    config = config or Configuracion.desde_entorno()
    app = FastAPI(title="EduTech Academy · API de lógica de negocio", version="1.0.0",
                  description="PIA de Componentes de Lógica de Negocio (FIME, UANL). Inscripciones, solicitudes, "
                              "asistencia, calificaciones, actas y certificados con las reglas del BRD de "
                              "EduTech Academy. Usuarios de demostración para X-Usuario: inst-1 (Instructor), "
                              "ce-1 (Control Escolar), coord-1 (Coordinación Académica).")
    estado = {"sistema": sistema}
    candado = threading.Lock()      # una conexión compartida: las peticiones se atienden de una en una

    def iniciar() -> Sistema:
        s = Sistema(config.roles, config.database_url)
        if config.cargar_datos_demo and base_vacia(s):
            cargar_datos(s, config.datos_dir)
        return s

    def usar(funcion):
        with candado:
            if estado["sistema"] is None:
                estado["sistema"] = iniciar()
            return funcion(estado["sistema"])

    @app.exception_handler(ErrorDeDominio)
    @app.exception_handler(AccesoDenegado)
    def error_de_negocio(_: Request, exc: Exception):
        codigo = next(c for tipo, c in ESTADO_HTTP if isinstance(exc, tipo))
        return JSONResponse(status_code=codigo, content={"mensaje": str(exc)})

    @app.exception_handler(RequestValidationError)
    def peticion_mal_formada(_: Request, exc: RequestValidationError):
        e = exc.errors()[0]
        campo = ".".join(str(x) for x in e["loc"][1:]) or "cuerpo"
        texto = (f"Falta el dato '{campo}' en la petición." if e["type"] == "missing"
                 else f"El dato '{campo}' no es válido: {e['msg']}.")
        return JSONResponse(status_code=400, content={"mensaje": texto})

    @app.exception_handler(IntegrityError)
    def duplicado(_: Request, exc: IntegrityError):
        return JSONResponse(status_code=409, content={"mensaje": "El registro ya existe (dato único duplicado)."})

    # ---------------- General ----------------
    @app.get("/", include_in_schema=False)
    def inicio():
        return RedirectResponse("/docs")

    @app.get("/salud", tags=["General"])
    def salud():
        return usar(lambda s: {"estado": "ok", "entorno": config.entorno,
                               "baseDeDatos": s.db.engine.dialect.name,
                               "solicitudes": len(s.solicitudes.todas())})

    @app.post("/demo/reiniciar", tags=["General"], summary="Vuelve a cargar los datos del paquete (demostración)")
    def reiniciar():
        def accion(s):
            from ..infrastructure.sql import metadata
            metadata.drop_all(s.db.engine)
            s.cerrar()
            estado["sistema"] = None
            nuevo = Sistema(config.roles, config.database_url)
            reporte = cargar_datos(nuevo, config.datos_dir)
            estado["sistema"] = nuevo
            return {"mensaje": "Datos de demostración cargados.", "estudiantes": reporte.estudiantes,
                    "cursos": reporte.cursos, "solicitudes": reporte.solicitudes,
                    "cuposAjustadosINV03": reporte.cuposAjustados}
        with candado:
            if estado["sistema"] is None:
                estado["sistema"] = iniciar()
            return accion(estado["sistema"])

    # ---------------- Catálogo ----------------
    def curso_dto(s, c) -> dict:
        g = s.grupos.obtener(grupoDelCurso(c.cursoId))
        return {"cursoId": c.cursoId, "nombre": c.nombre, "modalidad": c.modalidad.value, "precio": c.costo,
                "habilitado": c.habilitado, "grupoId": g.grupoId, "cupo": g.cupo.capacidad,
                "ocupados": len(g.ocupados), "disponibles": g.cupo.capacidad - len(g.ocupados)}

    @app.get("/estudiantes", tags=["Catálogo"], response_model=list[E.EstudianteOut])
    def estudiantes():
        return usar(lambda s: [vars(e) for e in s.estudiantes.todos()])

    @app.get("/estudiantes/{estudianteId}", tags=["Catálogo"], response_model=E.EstudianteOut, responses=ERRORES)
    def estudiante(estudianteId: str):
        return usar(lambda s: vars(s.estudiantes.obtener(estudianteId)))

    @app.get("/cursos", tags=["Catálogo"], response_model=list[E.CursoOut])
    def cursos():
        return usar(lambda s: [curso_dto(s, c) for c in s.cursos.todos()])

    @app.get("/cursos/{cursoId}", tags=["Catálogo"], response_model=E.CursoOut, responses=ERRORES)
    def curso(cursoId: str):
        return usar(lambda s: curso_dto(s, s.cursos.obtener(cursoId)))

    # ---------------- Solicitudes (paquete de datos, máquina de estados) ----------------
    @app.get("/solicitudes", tags=["Solicitudes"], response_model=list[E.SolicitudOut])
    def solicitudes(estado: str | None = None):
        return usar(lambda s: [solicitud_dto(x) for x in s.solicitud.listar(estado)])

    @app.post("/solicitudes", tags=["Solicitudes"], status_code=201, response_model=E.SolicitudConMensaje,
              responses=ERRORES, summary="Registrar una solicitud (queda en Preinscrito)")
    def registrar(datos: E.SolicitudIn):
        cmd = RegistrarSolicitud(datos.estudianteId, [(c.cursoId, c.lugares) for c in datos.cursos],
                                 datos.fecha or date.today(), datos.autorizada, datos.promocionActiva)
        return usar(lambda s: {"mensaje": "Solicitud registrada en Preinscrito.",
                               **solicitud_dto(s.solicitud.registrar(cmd))})

    @app.get("/solicitudes/{solicitudId}", tags=["Solicitudes"], response_model=E.SolicitudOut, responses=ERRORES)
    def solicitud(solicitudId: str):
        return usar(lambda s: solicitud_dto(s.solicitud.obtener(solicitudId)))

    @app.get("/solicitudes/{solicitudId}/evaluacion", tags=["Solicitudes"], response_model=E.EvaluacionOut,
             responses=ERRORES, summary="Evaluar las Specifications sin cambiar la solicitud")
    def evaluar(solicitudId: str):
        def accion(s):
            ev = s.solicitud.evaluar(solicitudId)
            return {**vars(ev), "reglas": {"puedeProcesarse": PUEDE_PROCESARSE.nombre,
                                           "beneficioReferencia": BENEFICIO_REFERENCIA.nombre}}
        return usar(accion)

    def transicion(solicitudId: str, accion, texto: str):
        return usar(lambda s: {"mensaje": texto.format(solicitudId), **solicitud_dto(accion(s))})

    @app.post("/solicitudes/{solicitudId}/formalizar", tags=["Solicitudes"], response_model=E.SolicitudConMensaje,
              responses=ERRORES, summary="Preinscrito → Inscrito (reglas + reserva de lugares)")
    def formalizar(solicitudId: str):
        return transicion(solicitudId, lambda s: s.solicitud.formalizar(solicitudId),
                          "Solicitud {} formalizada: estado Inscrito.")

    @app.post("/solicitudes/{solicitudId}/concluir", tags=["Solicitudes"], response_model=E.SolicitudConMensaje,
              responses=ERRORES, summary="Inscrito → Concluido")
    def concluir(solicitudId: str):
        return transicion(solicitudId, lambda s: s.solicitud.concluir(solicitudId),
                          "Solicitud {} concluida.")

    @app.post("/solicitudes/{solicitudId}/cancelar", tags=["Solicitudes"], response_model=E.SolicitudConMensaje,
              responses=ERRORES, summary="Preinscrito → Liberada")
    def cancelar(solicitudId: str, datos: E.CancelacionIn | None = None):
        motivo = (datos or E.CancelacionIn()).motivo
        return transicion(solicitudId, lambda s: s.solicitud.cancelar(solicitudId, motivo),
                          "Solicitud {} cancelada: estado Liberada.")

    # ---------------- CU-01 Inscripción a un grupo ----------------
    @app.post("/grupos/{grupoId}/inscripciones", tags=["CU-01 Inscripción"], status_code=201,
              response_model=E.InscripcionOut, responses={202: {"model": E.InscripcionOut}, **ERRORES},
              summary="Solicitar inscripción: Preinscrito o lista de espera si no hay cupo")
    def inscribir(grupoId: str, datos: E.DatosContactoIn):
        contacto = {"nombre": datos.nombre, "correo": datos.correo, "telefono": datos.telefono}
        cmd = SolicitarInscripcion(datos.estudianteId, grupoId, contacto, datos.ahora or datetime.now())
        r = usar(lambda s: s.inscripcion.solicitarInscripcion(cmd))
        if isinstance(r, EnListaDeEspera):
            return JSONResponse(status_code=202, content={"mensaje": "Grupo lleno: quedó en lista de espera.",
                                                          "estado": "En lista de espera"})
        return {"mensaje": "Solicitud registrada: estado Preinscrito.", "inscripcionId": r.inscripcionId,
                "estado": r.estado, "monto": r.monto, "fechaLimitePago": r.fechaLimitePago}

    @app.post("/inscripciones/{inscripcionId}/pagos", tags=["CU-01 Inscripción"], response_model=E.InscripcionOut,
              responses=ERRORES, summary="Pago acreditado por el sistema contable (50 % formaliza)")
    def pagar(inscripcionId: str, datos: E.PagoIn):
        def accion(s):
            evento = s.contable.pagoNotificado(inscripcionId, datos.monto, datos.fecha or date.today())
            i = s.inscripciones.obtener(inscripcionId)
            texto = f"Inscripción formalizada con folio {evento.folio}." if evento else "Abono registrado."
            return {"mensaje": texto, "inscripcionId": inscripcionId, "estado": i.estado.value,
                    "monto": i.monto, "fechaLimitePago": i.fechaLimitePago}
        return usar(accion)

    @app.get("/inscripciones/{inscripcionId}/estado-de-pago", tags=["CU-01 Inscripción"],
             response_model=E.EstadoDePagoOut, responses=ERRORES)
    def estado_de_pago(inscripcionId: str):
        return usar(lambda s: vars(s.estadoDePago.consultarEstadoDePago(inscripcionId)))

    @app.post("/inscripciones/{inscripcionId}/vencimiento", tags=["CU-01 Inscripción"], responses=ERRORES,
              summary="Revisar el plazo de pago: si venció, libera el lugar y avisa al siguiente")
    def vencimiento(inscripcionId: str, datos: E.VencimientoIn | None = None):
        ahora = (datos.ahora if datos else None) or datetime.now()
        eventos = usar(lambda s: s.inscripcion.liberarPorPlazoVencido(inscripcionId, ahora))
        return {"mensaje": "Plazo vencido: lugar liberado." if eventos else "El plazo de pago sigue vigente.",
                "eventos": [type(e).__name__ for e in eventos]}

    # ---------------- CU-02 Asistencia y CU-03 Calificaciones ----------------
    @app.post("/inscripciones/{inscripcionId}/asistencias", tags=["CU-02 Asistencia"], responses=ERRORES)
    def asistencia(inscripcionId: str, datos: E.AsistenciaIn, usuario: Usuario):
        pct = usar(lambda s: s.asistencia.registrarAsistencia(inscripcionId, datos.sesion, datos.presente,
                                                              usuario, datos.ahora or datetime.now()))
        return {"mensaje": f"Asistencia de la sesión {datos.sesion} registrada.", "porcentajeAsistencia": pct}

    @app.post("/inscripciones/{inscripcionId}/evaluaciones", tags=["CU-03 Calificaciones"], responses=ERRORES)
    def evaluacion(inscripcionId: str, datos: E.EvaluacionIn, usuario: Usuario):
        final = usar(lambda s: s.calificacion.capturarEvaluacion(inscripcionId, datos.clave, datos.tipo,
                                                                 datos.valor, usuario))
        return {"mensaje": "Evaluación capturada.", "calificacionFinal": final}

    # ---------------- CU-04 Acta y CU-05 Certificados ----------------
    @app.post("/grupos/{grupoId}/acta/cierre", tags=["CU-04 Acta"], response_model=E.ActaOut, responses=ERRORES)
    def cerrar_acta(grupoId: str, datos: E.CierreActaIn | None = None):
        hoy = (datos.hoy if datos else None) or date.today()
        acta = usar(lambda s: s.acta.cerrarActa(grupoId, hoy))
        return {"grupoId": acta.grupoId, "estado": acta.estado.value, "fechaCierre": acta.fechaCierre,
                "lineas": [vars(linea) for linea in acta.lineas]}

    @app.post("/certificados", tags=["CU-05 Certificados"], status_code=201, response_model=E.CertificadoOut,
              responses=ERRORES)
    def emitir(datos: E.CertificadoIn, usuario: Usuario):
        c = usar(lambda s: s.certificado.emitirCertificado(datos.grupoId, datos.inscripcionId, usuario,
                                                           datos.hoy or date.today()))
        return {"folio": c.folio, "titular": c.titular, "curso": c.curso, "fechaConclusion": c.fechaConclusion,
                "codigoQr": c.codigoQr, "dentroDePlazo": c.dentroDePlazo}

    @app.get("/verificacion/{folio}", tags=["CU-05 Certificados"], response_model=E.VerificacionOut,
             responses=ERRORES, summary="Verificación pública sin credenciales")
    def verificar(folio: str):
        return usar(lambda s: vars(s.verificacion.consultarCertificado(folio)))

    return app


app = crear_app()
