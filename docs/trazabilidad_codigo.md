# Trazabilidad regla → componente → prueba (lado del código)

Base para la matriz BRD → User Story → regla → componente → prueba. Las columnas de BRD y User Story/Gherkin las completa el equipo de análisis con los IDs de `docs/BRD.md`. Cada regla tiene su ID en un comentario del código, por eso se puede buscar: `grep -rn "INV-11" src tests`.

| Regla | Qué dice | Componente (src/) | Endpoint | Pruebas (tests/) |
|---|---|---|---|---|
| INV-01 | La ponderación suma 100 (40/40/20) | `domain/valores.py` Ponderacion | — | `unit/test_dominio_u3.py::test_INV01_…` |
| INV-02, INV-21 | Criterio Regular (70 y 80 %) u Oficial (80 y 90 %); calificación Y asistencia | `domain/valores.py` CriterioDeCertificacion.regla() (Specification) | `POST /grupos/{id}/acta/cierre` | `unit/test_especificaciones.py::test_INV21_…`, `unit/test_dominio_u3.py::test_INV21_…` |
| INV-03 | Cupo 25 presencial / 40 en línea; sobrecupo ≤ 10 % | `domain/grupo.py` reservarLugar, `domain/valores.py` Cupo, `infrastructure/carga_csv.py` | `POST /grupos/{id}/inscripciones`, `POST /solicitudes/{id}/formalizar` | `unit/test_dominio_u3.py::test_INV03_…`, `integration/test_solicitud_service.py::test_sin_cupo_…`, `integration/test_paquete_profesor.py::test_carga_aplica_INV03_…` |
| INV-04 | Lugar liberado se ofrece al primero de la lista por 24 h | `domain/grupo.py` liberarLugar, `application/inscripcion_service.py` | `POST /inscripciones/{id}/vencimiento` | `unit/test_dominio_u3.py::test_INV04_…`, `integration/test_api.py::test_lista_de_espera_y_vencimiento` |
| REG-01 | Solicitud con nombre, correo y teléfono | `domain/inscripcion.py` preinscribir | `POST /grupos/{id}/inscripciones` | `unit/test_dominio_u3.py::test_REG01_…`, `integration/test_servicios_u3.py::test_datos_incompletos_…` |
| INV-06, 07, 08 | 50 % pagado formaliza; menos es abono; folio único | `domain/inscripcion.py` registrarPago | `POST /inscripciones/{id}/pagos` | `unit/test_dominio_u3.py::test_INV06_INV08_…`, `::test_INV07_…` |
| INV-09 | Plazo de pago 7 días; prórroga | `domain/inscripcion.py` vencerPlazo | `POST /inscripciones/{id}/vencimiento` | `unit/test_dominio_u3.py::test_INV09_…`, `integration/test_servicios_u3.py::test_SEQ02_…` |
| INV-11 | Instructor registra asistencia dentro de 48 h | `domain/expediente.py` registrarAsistencia | `POST /inscripciones/{id}/asistencias` | `unit/test_dominio_u3.py::test_INV11_…`, `integration/test_api.py::test_permisos_y_ventana_de_48_horas` |
| INV-12 | En línea: 60 % de conexión O grabación en 72 h | `domain/especificaciones.py` ASISTENCIA_EN_LINEA | (LMS adapter) | `unit/test_especificaciones.py::test_INV12_…` |
| INV-13 | Solo 2 justificaciones por curso | `domain/expediente.py` justificarInasistencia | — | `unit/test_dominio_u3.py::test_INV13_…` |
| INV-14, 16, 17 | Evaluación 0–100; solo Inscrito; no modificar la de otro instructor | `domain/expediente.py`, `domain/valores.py` Evaluacion | `POST /inscripciones/{id}/evaluaciones` | `unit/test_dominio_u3.py::test_INV14_INV16_INV17_…`, `integration/test_api.py` |
| INV-15 | Calificación final ponderada | `domain/expediente.py` calificacionFinal | `POST /inscripciones/{id}/evaluaciones` | `unit/test_dominio_u3.py::test_INV15_…` |
| INV-18, 19, 20, 22 | Acta: 5 días hábiles, sin sesiones vacías, solo Inscrito, cerrada no cambia | `domain/acta.py`, `application/acta_service.py` | `POST /grupos/{id}/acta/cierre` | `integration/test_servicios_u3.py::test_CU04_…`, `integration/test_api.py::test_curso_completo_por_la_api` |
| INV-23, 24, 25 | Certificado: acta cerrada y cumple; autoriza Coordinación; folio único en 10 días hábiles | `domain/certificado.py`, `application/certificado_service.py`, UNIQUE en `infrastructure/sql.py` | `POST /certificados`, `GET /verificacion/{folio}` | `integration/test_servicios_u3.py::test_CU04_CU05_…`, `integration/test_api.py::test_curso_completo_por_la_api` |
| D-06 | El servicio comprueba el rol | `application/puertos.py` exigirRol | encabezado `X-Usuario` | `integration/test_integracion_u5.py::test_PIA19_…` a `PIA21` |
| PKG-1 | Puede procesarse: activo Y con cursos Y autorizada | `domain/especificaciones.py` PUEDE_PROCESARSE, `domain/solicitud.py` formalizar | `GET /solicitudes/{id}/evaluacion`, `POST …/formalizar` | `unit/test_especificaciones.py`, `integration/test_paquete_profesor.py::test_casos_prueba_del_paquete` (60 casos T) |
| PKG-2 | Beneficio: preferente Y total ≥ 1500 Y NO promoción | `domain/especificaciones.py` BENEFICIO_REFERENCIA | `GET /solicitudes/{id}/evaluacion` | `integration/test_paquete_profesor.py::test_casos_prueba_del_paquete` (60 casos B) |
| PKG-3 | Máquina de estados de la solicitud | `domain/solicitud.py` | `POST /solicitudes/{id}/formalizar · concluir · cancelar` | `unit/test_solicitud.py`, `integration/test_paquete_profesor.py::test_transiciones_del_paquete` (20) |

PKG = regla del paquete de datos del profesor adaptada a EduTech (ADR-007).
