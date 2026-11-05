# Mapeo del paquete de datos del profesor al dominio de EduTech

El paquete `15_EduTech_Academy/01_Alumno/datos` se carga con `src/infrastructure/carga_csv.py`. Los datos pasan por las reglas de EduTech; no se copian los estados ni las reglas del paquete.

| Archivo | Se convierte en | Reglas que se aplican al cargar o al procesar |
|---|---|---|
| `actores.csv` (40) | `Estudiante` (`preferente`, `activo`) | Un estudiante inactivo no formaliza (PUEDE_PROCESARSE) |
| `catalogo.csv` (20) | `Curso` (precio Decimal, `habilitado`) + `Grupo G-<curso>` | INV-03: cupo máximo 40 en línea; 4 cursos se ajustan. Curso deshabilitado → `CursoNoDisponible` |
| `operaciones.csv` (60) | `SolicitudDeInscripcion` en **Preinscrito** | Autorización y promoción se guardan en la solicitud |
| `detalle_operaciones.csv` (117) | Líneas: curso × lugares | 1 a 10 lugares por curso; total = Σ precio × lugares con Decimal |
| `casos_prueba.csv` (120) | `validar_operacion` → `PUEDE_PROCESARSE`; `evaluar_beneficio` → `BENEFICIO_REFERENCIA` | Resultado en `evidencias/resultados_casos_prueba.csv` |
| `transiciones_prueba.csv` (20) | Acciones de la máquina de estados | Resultado en `evidencias/resultados_transiciones.csv` |

## Acciones del paquete

| Acción | En EduTech | Resultado esperado |
|---|---|---|
| `aprobar` | `formalizar` | Preinscrito → Inscrito, evento `SolicitudFormalizada`, folio `INS-<id>`, lugares reservados |
| `completar` | `formalizar` + `concluir` | → Concluido, evento `SolicitudConcluida` |
| `cancelar` | `cancelar` | Preinscrito → Liberada, evento `SolicitudLiberada` |
| `repetir_aprobacion` | `formalizar` dos veces | La segunda: `TransicionNoPermitida` (409), un solo evento |
| `saltar_estado` | `concluir` desde Preinscrito | `TransicionNoPermitida` (409), sin cambios |

## Datos con errores intencionales del paquete
5 estudiantes inactivos · 7 operaciones sin autorización · 2 operaciones sin líneas (EDU-O013, EDU-O039) · 6 con promoción · 1 curso deshabilitado (EDU-P011).
