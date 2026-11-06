**Proyecto:** Plataforma de gestión académica y certificación de EduTech Academy

**Curso:** Componentes de Lógica de Negocios

**Institución:** FIME – UANL

**Responsable de esta sección:** Análisis del negocio y glosario

> *Criterio de lectura. Este BRD conserva las necesidades y reglas del BRD de la Unidad 2 y las precisiones del reporte de arquitectura de la Unidad 3. Distingue entre: (1) alcance del negocio, (2) alcance de los cinco casos de uso seleccionados en U3 y (3) evidencia de implementación en el repositorio. Que una capacidad esté dentro del alcance del negocio no significa que esté implementada en esta versión.*

## 1. Resumen y contexto del negocio

EduTech Academy ofrece programas de capacitación profesional presenciales y en línea. Atiende a estudiantes individuales mediante grupos abiertos y a organizaciones que contratan capacitación empresarial.

De acuerdo con el levantamiento de la Unidad 2, procesos como inscripción, control de asistencia, consolidación de actas, emisión y validación de certificados se apoyan en procedimientos manuales y archivos distribuidos, principalmente hojas de cálculo. Esta fragmentación ocasiona demoras, errores de captura y dificultad para identificar oportunamente a estudiantes que podrían no cumplir los criterios de certificación.

El proyecto plantea centralizar la información y automatizar reglas relacionadas con cursos, grupos, solicitudes e inscripciones, pagos, asistencia, evaluaciones, actas y certificados. También contempla la consulta pública de autenticidad de certificados mediante folio o código QR.

## 2. Problema y oportunidad

### 2.1 Problemas identificados en la Unidad 2

- La validación de autenticidad de certificados puede tomar entre uno y tres días hábiles mediante correo y búsqueda manual.

- La consolidación manual de actas presenta un margen de error aproximado del 8%.

- La emisión y entrega de un certificado puede tardar hasta 15 días hábiles después del cierre del acta.

- Identificar estudiantes en riesgo requiere entre cuatro y seis horas de procesamiento manual por corte.

Estas cifras son datos reportados durante el levantamiento; no son resultados medidos por el sistema desarrollado.

### 2.2 Oportunidad

Centralizar la operación académica y aplicar reglas consistentes para reducir errores, facilitar el seguimiento del desempeño y habilitar la verificación pública de certificados. Las metas de negocio se detallan en la sección 11.

## 3. Objetivos del negocio

1.  Centralizar la información de cursos, grupos, estudiantes, inscripciones, pagos, asistencias, evaluaciones, actas y certificados.

2.  Aplicar consistentemente las reglas de cupo, inscripción, asistencia, evaluación y certificación.

3.  Reducir errores derivados de la captura y consolidación manual de información académica.

4.  Facilitar la identificación de estudiantes que están en riesgo de no cumplir los criterios de certificación.

5.  Permitir la verificación pública de certificados mediante folio o código QR sin requerir credenciales.

6.  Mejorar la trazabilidad de operaciones y autorizaciones administrativas y académicas.

## 4. Stakeholders

| **Stakeholder**           | **Responsabilidad o interés**                                                                                         |
|---------------------------|-----------------------------------------------------------------------------------------------------------------------|
| Estudiante / Participante | Solicita inscripción, realiza pagos, asiste, presenta evaluaciones y consulta su información y certificado.           |
| Instructor                | Imparte el curso, registra asistencia y captura evaluaciones conforme a las reglas y plazos.                          |
| Control Escolar           | Gestiona justificaciones, correcciones autorizadas, consolidación académica y revisión del cumplimiento de criterios. |
| Coordinación Académica    | Aprueba programas, define criterios y ponderaciones, autoriza certificados y gestiona sustituciones académicas.       |
| Administración            | Gestiona pagos, prórrogas, sobrecupos autorizados y compensaciones por cancelación.                                   |
| Cliente empresarial       | Formaliza convenios, entrega listas de participantes y recibe reportes de avance y resultados.                        |
| Terceros / Empleadores    | Consultan la autenticidad y vigencia de certificados.                                                                 |

## 5. Alcance del negocio

### 5.1 Dentro del alcance de negocio (Unidad 2)

- **Gestión de inscripciones:** registro de solicitudes, validación de requisitos y cupos, asignación de folio y lista de espera.

- **Gestión de pagos e integración:** recepción del estado de acreditación informado por el sistema contable y formalización de la inscripción.

- **Control de asistencia:** registro presencial, acreditación de asistencia en línea y gestión de justificaciones.

- **Evaluación y calificaciones:** captura de evaluaciones, cálculo ponderado, examen de recuperación y consolidación de actas.

- **Certificación y verificación:** emisión de certificados con folio único y QR, consulta pública y constancias de participación.

- **Capacitación empresarial:** flujo bajo convenio, bajas y sustituciones de participantes, y reportes en PDF/Excel.

- **Excepciones y cambios:** cancelaciones, reembolsos o créditos, cambios de grupo y sustitución de instructores.

- **Recursamiento:** posibilidad de volver a cursar dentro de los seis meses posteriores con 50% de descuento.

### 5.2 Casos de uso delimitados en la Unidad 3

La Etapa 1 de U3 seleccionó cinco casos de uso:

| **ID** | **Caso de uso**                                                        | **Actor principal** |
|--------|------------------------------------------------------------------------|---------------------|
| CU-01  | Gestión de inscripción y cupos                                         | Estudiante          |
| CU-02  | Control de asistencia                                                  | Instructor          |
| CU-03  | Actualización de calificaciones                                        | Instructor          |
| CU-04  | Consolidación del desempeño y cierre de acta / evaluación de criterios | Control Escolar     |
| CU-05  | Validación pública inmediata de certificado                            | Empleador / tercero |

**Importante:** U3 indica que cancelación de curso, cambio de grupo, recursamiento, examen de recuperación, constancia de participación, cliente empresarial y convenio no forman parte de estos cinco casos de uso. Algunas reglas de esas capacidades se conservan como requisitos del negocio, pero no deben presentarse como funciones implementadas por la versión demostrada.

La emisión del certificado se describe en US-15 y cuenta con servicio en el repositorio; sin embargo, el reporte de U3 aclara que la emisión no tiene un caso de uso independiente dentro de los cinco seleccionados. CU-04 habilita la emisión y CU-05 cubre la consulta pública.

### 5.3 Fuera del alcance

- Emisión de facturación fiscal.

- Procesamiento directo de nómina o pago a instructores.

- Diseño y gestión de contenidos pedagógicos.

- Estrategias, campañas y herramientas de marketing o captación de prospectos.

## 6. Necesidades y reglas del negocio

### 6.1 Inscripción, pago y cupo

7.  La formalización requiere datos obligatorios completos, lugar disponible y pago acreditado.

8.  La primera parcialidad del 50% del monto permite pasar de Preinscrito a Inscrito; un pago menor se registra como abono y conserva el estado Preinscrito.

9.  El plazo ordinario de pago es de siete días naturales desde el inicio del curso. Administración puede autorizar una prórroga.

10. La Unidad 2 también menciona una tolerancia de dos sesiones con pago pendiente. La relación exacta entre esa tolerancia y el plazo de siete días debe confirmarse con el stakeholder.

11. Los grupos tienen un mínimo de ocho inscritos y máximos de 25 participantes presenciales y 40 en línea.

12. El sobrecupo puede ser de hasta 10% con autorización de Administración. El guion de U3 limita esta posibilidad a modalidad en línea, mientras el BRD de U2 no especifica modalidad. Se requiere una decisión formal.

13. La lista de espera se ordena por fecha y hora. Cuando se libera un lugar, se ofrece al primero con una ventana de 24 horas para confirmar o pagar.

14. El folio de inscripción se genera al formalizarse y debe ser único.

### 6.2 Asistencia y justificaciones

15. El instructor puede registrar o corregir asistencia dentro de las 48 horas posteriores a la sesión.

16. Después de ese plazo, la corrección corresponde a Control Escolar y requiere justificación escrita del instructor.

17. En modalidad en línea se acredita la asistencia con al menos 60% de conexión en vivo o al visualizar la grabación dentro de las 72 horas siguientes.

18. Se permiten hasta dos justificaciones por curso que no cuentan contra el porcentaje de asistencia. Deben presentarse dentro de cinco días hábiles; desde la tercera, la falta cuenta para el porcentaje.

### 6.3 Evaluación y certificación

19. La ponderación estándar es 40% evaluaciones parciales, 40% proyecto final y 20% actividades/participación.

20. Coordinación Académica puede autorizar una ponderación distinta, que debe quedar registrada en el Curso antes de abrir el Grupo.

21. Criterio Regular: calificación mínima de 70/100 y asistencia mínima de 80%.

22. Criterio Oficial: calificación mínima de 80/100 y asistencia mínima de 90%.

23. La calificación final se calcula mediante la ponderación del Curso; no debe capturarse manualmente como sustituto del cálculo.

24. Solo las inscripciones en estado Inscrito forman parte del acta.

25. El acta se cierra a los cinco días hábiles de la última sesión y no puede cerrarse si existen sesiones sin asistencia capturada.

26. Un acta cerrada no se modifica; U3 señala que una corrección requeriría una apertura formal autorizada por Coordinación Académica. El reporte del repositorio implementa el bloqueo del acta cerrada, pero no documenta un flujo de reapertura.

27. La emisión requiere acta cerrada, estudiante que cumple los criterios y autorización de Coordinación Académica. Se registra el usuario autorizante.

28. El certificado tiene folio único y debe publicarse dentro de diez días hábiles después del cierre del acta.

### 6.4 Excepciones y procesos complementarios

- **Cancelación:** si no se alcanza el mínimo de ocho inscritos a tres días hábiles del inicio, Administración puede cancelar el curso. El BRD ofrece reembolso del 100%, crédito a favor o cambio de grupo. US-16 precisa crédito por 12 meses y un plazo de atención de reembolso de 10 días hábiles.

- **Cambio de grupo:** permitido hasta 30% de avance, para el mismo curso y periodo. U3 agrega una sola solicitud por inscripción y disponibilidad en el grupo destino. No tiene CU en la Etapa 1.

- **Recursamiento:** 50% de descuento para volver a cursar dentro de los seis meses posteriores.

- **Examen de recuperación:** solo en cursos regulares, para calificación entre 60 y 69 y asistencia mínima de 80%.

- **Sustitución de instructor:** el instructor entrante no puede modificar las evaluaciones capturadas por su predecesor; las correcciones pasan por Control Escolar con justificación.

- **Cliente empresarial:** opera mediante convenio, con listas de participantes y reportes de avance quincenales/finales. El BRD establece facturación a 30 días contra entrega de convenio/lista; la facturación fiscal permanece fuera del alcance del sistema.

### 6.5 Verificación pública

La consulta por folio o QR debe estar disponible sin autenticación. Debe mostrar titular, curso, fecha de conclusión y vigencia/estatus del certificado. No debe exponer datos de contacto ni calificaciones. U3 ubica esta regla en el modelo de lectura y no como invariante del Aggregate Certificado.

## 7. Requerimientos funcionales

Los identificadores RF se asignan para organizar este BRD; no sustituyen los IDs originales US, CU o INV.

| **ID** | **Requerimiento funcional**                                                                           | **Trazabilidad principal**    | **Alcance de versión**                                                                            |
|--------|-------------------------------------------------------------------------------------------------------|-------------------------------|---------------------------------------------------------------------------------------------------|
| RF-01  | Consultar catálogo de cursos, modalidad, calendario, costo y cupo disponible.                         | US-01                         | Repositorio: consulta de cursos; confirmar correspondencia completa de calendario en UI.          |
| RF-02  | Consultar requisitos y criterios Regular/Oficial.                                                     | US-02                         | Dominio define criterios; presentación al estudiante no está acreditada por el API.               |
| RF-03  | Consultar cupo y rechazar reservas que excedan capacidad permitida.                                   | US-03, INV-03                 | Implementado en dominio/API.                                                                      |
| RF-04  | Registrar solicitud con datos obligatorios y estado Preinscrito; usar lista de espera si no hay cupo. | US-04, INV-04, REG-01         | Implementado en servicios/API.                                                                    |
| RF-05  | Registrar pagos acreditados, formalizar con 50% o más y conservar Preinscrito con abonos menores.     | US-05, INV-06 a INV-08        | Implementado; el pago entra mediante adaptador contable.                                          |
| RF-06  | Consultar estado de pago, saldo y fecha límite.                                                       | US-06, INV-09                 | Implementado como consulta/servicio; la liberación requiere ejecutar la operación de vencimiento. |
| RF-07  | Consultar grupo, calendario, modalidad, instructor y asistencia acumulada.                            | US-07                         | Datos de grupo existen; confirmar cobertura completa de consulta.                                 |
| RF-08  | Solicitar y gestionar cambio de grupo sujeto a límites de negocio.                                    | US-08, US-09, INV-10          | No implementado en la versión revisada; sin CU en U3.                                             |
| RF-09  | Consultar lista de participantes y señalar pagos pendientes.                                          | US-10, INV-16                 | Cobertura parcial en servicios/modelo; no asumir pantalla de instructor.                          |
| RF-10  | Registrar asistencia dentro de 48 horas y gestionar corrección extemporánea por Control Escolar.      | US-11, INV-11, INV-12, INV-13 | Implementado en servicios de asistencia; integración LMS real no acreditada.                      |
| RF-11  | Capturar evaluaciones válidas y calcular calificación ponderada.                                      | US-12, INV-14 a INV-17        | Implementado en dominio/servicios.                                                                |
| RF-12  | Consultar desempeño consolidado y señalar sesiones sin asistencia.                                    | US-13, INV-19, INV-20         | Consolidador/acta implementados; no implica tablero visual completo.                              |
| RF-13  | Evaluar cumplimiento de criterios Regular u Oficial e indicar motivo.                                 | US-14, INV-02, INV-21         | Implementado en dominio y consolidación.                                                          |
| RF-14  | Cerrar acta bajo las condiciones y plazos establecidos.                                               | US-13, US-15, INV-18 a INV-22 | Implementado el cierre y bloqueo posterior; flujo formal de reapertura no implementado.           |
| RF-15  | Emitir certificado con folio único, autorización y plazo de publicación.                              | US-15, INV-23 a INV-25        | Servicio implementado; verificar publicación/despliegue y vigencia.                               |
| RF-16  | Cancelar cursos y registrar compensaciones a participantes.                                           | US-16, INV-05                 | No implementado en los cinco CU revisados.                                                        |
| RF-17  | Registrar sustitución de instructor y proteger evaluaciones previas.                                  | US-17, INV-17                 | Regla de protección de evaluaciones implementada; flujo completo de sustitución no acreditado.    |
| RF-18  | Generar reportes operativos de inscripciones, pagos y avance.                                         | US-18                         | Consulta de estado disponible; reporte completo no acreditado.                                    |
| RF-19  | Verificar públicamente certificado por folio sin credenciales ni exposición de datos sensibles.       | US-19, REG-02                 | Implementado como endpoint/modelo de lectura.                                                     |
| RF-20  | Identificar estudiantes en riesgo de no certificar durante el curso.                                  | US-20                         | No se encontró implementación específica acreditada en el repositorio revisado.                   |

## 8. Requerimientos no funcionales y restricciones de calidad

El BRD original contiene restricciones y expectativas de calidad, pero no define métricas técnicas para todas ellas. Para evitar inventar compromisos, esta tabla separa lo expresamente establecido de los criterios propuestos que el equipo debe aprobar.

| **ID** | **Requerimiento / expectativa**                                                                    | **Criterio de verificación**                                                                                               | **Estado**                                                                                                                     |
|--------|----------------------------------------------------------------------------------------------------|----------------------------------------------------------------------------------------------------------------------------|--------------------------------------------------------------------------------------------------------------------------------|
| RNF-01 | La verificación pública debe ser accesible sin autenticación.                                      | Consultar un folio válido sin enviar credenciales y obtener la respuesta pública permitida.                                | Requisito explícito; endpoint disponible en código.                                                                            |
| RNF-02 | La verificación pública no debe exponer contacto ni calificaciones.                                | Revisar el DTO/respuesta y probar que esos campos no aparecen.                                                             | Requisito explícito; modelo de lectura restringido en código.                                                                  |
| RNF-03 | Las operaciones protegidas deben validar el rol correspondiente.                                   | Probar acceso permitido y denegado para los roles definidos.                                                               | Requisito derivado de reglas; servicio de acceso por rol implementado.                                                         |
| RNF-04 | Los cambios de estado y operaciones compuestas deben conservar consistencia.                       | Pruebas de éxito y fallo que verifiquen confirmación o reversión de transacción.                                           | Criterio técnico propuesto; Unit of Work documentada e implementada.                                                           |
| RNF-05 | Los importes monetarios deben manejarse sin errores de precisión binaria.                          | Verificar cálculos y persistencia usando Decimal.                                                                          | Decisión técnica implementada; no es KPI de negocio.                                                                           |
| RNF-06 | La solución debe poder ejecutarse en entornos configurables y contenerizados.                      | Construcción de imagen y ejecución mediante Docker Compose.                                                                | ADR-008 y archivos de despliegue presentes; validar ejecución en entorno objetivo.                                             |
| RNF-07 | La automatización de pruebas debe cubrir al menos 80% del código.                                  | Reporte de cobertura generado por CI.                                                                                      | Meta indicada en ADR-008; la ejecución local del paquete revisado reportó 99%, con una prueba omitida que requiere PostgreSQL. |
| RNF-08 | La disponibilidad y el tiempo de respuesta de la plataforma deben ser adecuados para la operación. | Pendiente: el BRD no fija porcentaje de disponibilidad ni umbral técnico de respuesta. Acordar SLO antes de comprometerlo. | Por definir.                                                                                                                   |
| RNF-09 | Los datos personales y académicos deben protegerse según el rol y la finalidad de consulta.        | Pendiente: definir política de autenticación, autorización, retención y auditoría.                                         | El BRD establece restricciones de exposición pública, pero no una política completa.                                           |
| RNF-10 | Los plazos hábiles deben calcularse con un calendario institucional.                               | Probar fechas límite con fines de semana y días inhábiles configurados.                                                    | Servicio de calendario presente; calendario institucional real por confirmar.                                                  |

## 9. Supuestos y dependencias

- El sistema contable notificará de forma oportuna y confiable la acreditación de pagos.

- Los instructores contarán con dispositivos para registrar asistencia y evaluaciones dentro de los plazos establecidos.

- La plataforma LMS o de videoconferencia proporcionará datos de conexión y mantendrá grabaciones accesibles durante al menos 72 horas.

- La institución mantendrá un calendario de días inhábiles para los plazos administrativos y académicos.

- Los roles y autorizaciones serán administrados por mecanismos de control de acceso. El BRD define responsabilidades, pero no el mecanismo técnico de autenticación.

- Los flujos completos de capacitación empresarial y de excepciones requieren reglas y casos de uso adicionales si se incorporan a una siguiente versión.

## 10. Restricciones y políticas relevantes

- El instructor dispone de 48 horas para registrar o corregir asistencia por cuenta propia.

- Las justificaciones deben presentarse dentro de cinco días hábiles y están limitadas a dos por curso.

- Un instructor sustituto no puede modificar evaluaciones capturadas por su predecesor.

- La consulta pública de certificados no requiere autenticación y debe limitar los datos expuestos.

- La facturación empresarial se realiza a 30 días contra entrega de convenio/lista; la emisión de facturación fiscal está fuera del alcance.

- Los plazos de días hábiles dependen del calendario institucional.

- El BRD no define el periodo de vigencia del certificado; no debe asumirse que “Vigente” equivale a vigencia indefinida.

## 11. Criterios de éxito e indicadores

| **Indicador**                                   | **Situación actual reportada en U2** | **Meta de negocio**              |
|-------------------------------------------------|--------------------------------------|----------------------------------|
| Tiempo de validación pública de certificado     | 1 a 3 días hábiles                   | Menos de 1 minuto                |
| Margen de error en consolidación de actas       | Aproximadamente 8%                   | Menos del 1%                     |
| Tiempo total de emisión del certificado         | Hasta 15 días hábiles                | 5 días hábiles                   |
| Generación del reporte de estudiantes en riesgo | 4 a 6 horas manuales                 | Consulta en línea en tiempo real |

La evaluación formal de estos indicadores se plantea a los seis meses de la puesta en marcha. Existe una discrepancia que debe resolverse: el KPI establece una meta de cinco días hábiles para el tiempo total de emisión, mientras que INV-25 y US-15 establecen publicación dentro de diez días hábiles después del cierre del acta. No deben tratarse como el mismo plazo sin una decisión explícita del stakeholder.

## 12. Matriz de trazabilidad de negocio

La siguiente matriz enlaza las reglas de U3 con las historias de U2 y los casos de uso seleccionados. “Sin CU” significa que la historia/regla existe en el análisis del negocio, pero no fue incluida en los cinco casos de uso de U3.

| **Regla / requisito**                      | **Historia(s) de usuario**    | **Caso(s) de uso U3**                 | **Evidencia de implementación revisada**                                                                                                                 |
|--------------------------------------------|-------------------------------|---------------------------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------|
| INV-01 Ponderación                         | US-12                         | CU-03                                 | domain/valores.py; validación de suma 100. La autorización y el registro previo a abrir grupo deben verificarse en el flujo administrativo.              |
| INV-02 Criterios Regular/Oficial           | US-02, US-14                  | CU-01, CU-04                          | domain/valores.py; criterios definidos y usados al evaluar.                                                                                              |
| INV-03 Cupo y sobrecupo                    | US-03, US-09                  | CU-01                                 | domain/valores.py, domain/grupo.py; capacidad y límite de sobrecupo. La autorización del rol y la modalidad permitida requieren definición/verificación. |
| INV-04 Lista de espera                     | US-04, US-06                  | CU-01                                 | domain/grupo.py; orden por fecha/hora y ventana de 24 horas.                                                                                             |
| INV-05 Mínimo de ocho / cancelación        | US-16                         | Sin CU                                | No se encontró lógica específica de cancelación por mínimo de cupo en los cinco CU.                                                                      |
| INV-06 e INV-07 Formalización / abono      | US-05                         | CU-01                                 | domain/inscripcion.py; formaliza con 50% y conserva Preinscrito por debajo.                                                                              |
| INV-08 Folio de inscripción                | US-05                         | CU-01                                 | domain/inscripcion.py; folio asignado al formalizar. La unicidad global debe contrastarse con persistencia.                                              |
| INV-09 Vencimiento y prórroga              | US-06                         | CU-01                                 | domain/inscripcion.py, application/inscripcion_service.py; plazo y prórroga. La ejecución del vencimiento se invoca por operación/endpoint.              |
| INV-10 Cambio de grupo                     | US-08, US-09                  | Sin CU                                | No se encontró método/flujo de cambio de grupo en el código revisado.                                                                                    |
| INV-11 Asistencia en 48 h                  | US-11                         | CU-02                                 | domain/expediente.py, application/asistencia_service.py; captura y corrección por rol.                                                                   |
| INV-12 Asistencia en línea                 | US-11                         | CU-02                                 | domain/especificaciones.py, adaptador LMS; regla 60% o grabación en 72 h. Integración externa real por confirmar.                                        |
| INV-13 Justificaciones                     | Guion / BRD (sin US dedicada) | CU-02                                 | domain/expediente.py, application/asistencia_service.py; máximo dos y límite de cinco días hábiles.                                                      |
| INV-14 e INV-15 Evaluación y cálculo       | US-12                         | CU-03                                 | domain/valores.py, domain/expediente.py; rango 0–100 y cálculo ponderado.                                                                                |
| INV-16 Evaluaciones solo para Inscrito     | US-06, US-10 y guion          | CU-03                                 | domain/expediente.py; valida estado antes de capturar.                                                                                                   |
| INV-17 Protección de evaluación previa     | US-17                         | CU-03                                 | domain/expediente.py; impide que otro instructor sobrescriba la evaluación. Flujo completo de sustitución no acreditado.                                 |
| INV-18 Cierre a cinco días hábiles         | US-15                         | CU-04                                 | domain/acta.py, domain/servicios.py; calendario de días hábiles.                                                                                         |
| INV-19 No cerrar con asistencia incompleta | US-13                         | CU-04                                 | domain/acta.py, domain/servicios.py; bloquea cierre si faltan registros.                                                                                 |
| INV-20 Solo inscritos en acta              | US-06                         | CU-04                                 | domain/servicios.py; el consolidador recibe inscripciones formalizadas.                                                                                  |
| INV-21 Cumplimiento de criterios           | US-14                         | CU-04                                 | domain/valores.py, domain/servicios.py; combina calificación y asistencia.                                                                               |
| INV-22 Acta cerrada no modificable         | Guion (sin US dedicada)       | CU-04                                 | domain/acta.py y domain/expediente.py; bloqueo posterior al cierre. No se encontró flujo formal de reapertura.                                           |
| INV-23 a INV-25 Emisión de certificado     | US-15                         | CU-04 habilita; emisión sin CU propio | domain/certificado.py, application/certificado_service.py, persistencia SQL; acta cerrada, cumplimiento, rol, folio y plazo.                             |
| REG-01 Datos obligatorios                  | US-04                         | CU-01                                 | domain/inscripcion.py; valida nombre, correo y teléfono.                                                                                                 |
| REG-02 Consulta pública restringida        | US-19                         | CU-05                                 | application/puertos.py y modelo de lectura/API; respuesta pública limitada.                                                                              |
| Reporte operativo                          | US-18                         | Sin CU específico                     | Existe consulta de estado de pago; el reporte completo solicitado no se acredita como implementado.                                                      |
| Riesgo de certificación                    | US-20                         | Sin CU específico                     | No se encontró servicio específico de detección/reporte de riesgo en el código revisado.                                                                 |

## 13. Decisiones pendientes y riesgos de consistencia

| **Tema**                 | **Diferencia o vacío**                                                                                                  | **Acción requerida**                                                                                           |
|--------------------------|-------------------------------------------------------------------------------------------------------------------------|----------------------------------------------------------------------------------------------------------------|
| INV-05 / US-16           | Cancelación por mínimo de inscritos está en BRD y U2, pero fuera de los cinco CU y sin implementación acreditada.       | Mantener como alcance de negocio no implementado o agregar caso de uso/funcionalidad en una versión posterior. |
| INV-10 / US-08 y US-09   | Cambio de grupo está en BRD, pero no tiene CU en U3 ni flujo en el código revisado.                                     | No presentarlo como funcionalidad terminada.                                                                   |
| INV-03                   | U2 no restringe modalidad para sobrecupo; guion U3 lo limita a línea.                                                   | Obtener decisión explícita del stakeholder y actualizar BRD/glosario si cambia.                                |
| INV-09                   | U2 menciona tolerancia de dos sesiones y siete días naturales.                                                          | Definir cuál condición gobierna la liberación y qué ocurre si se cumplen en momentos distintos.                |
| INV-22                   | U3 exige apertura formal autorizada para corregir acta cerrada; código bloquea modificaciones, sin flujo de reapertura. | Definir si la reapertura se implementará o si queda fuera de versión.                                          |
| Vigencia del certificado | Se usa el término “vigencia”, pero U2 no establece duración ni evento de expiración.                                    | Definir duración, condición de revocación/expiración y significado del estatus público.                        |
| Plazo de certificado     | KPI de U2: cinco días; INV-25/US-15: publicación dentro de diez días hábiles tras cierre.                               | Aclarar si cinco días mide emisión interna y diez publicación, o corregir uno de los valores.                  |
| Integración contable/LMS | BRD los presenta como dependencias/supuestos.                                                                           | Diferenciar adaptadores o simulaciones de una integración productiva real.                                     |
| Calendario hábil         | No se especifica calendario institucional ni días inhábiles.                                                            | Definir quién mantiene el calendario y cómo se actualiza.                                                      |
| Seguridad y privacidad   | Consulta pública limitada; el mecanismo general de autenticación y auditoría no está detallado en U2.                   | Acordar política de acceso, protección y auditoría antes de producción.                                        |

## 14. Fuentes internas

- BRD EduTech Academy, Unidad 2, 10/09/2026.

- User Stories EduTech Academy, Unidad 2, 10/09/2026 (US-01 a US-20).

- Glosario EduTech Academy, Unidad 2, 10/09/2026.

- Reporte de arquitectura del sistema EduTech Academy, Unidad 3: casos de uso, fichas de Aggregates e invariantes INV-01 a INV-25, matriz de trazabilidad y decisiones dudosas.

- Repositorio edutech-academy-cln, especialmente src/domain/, src/application/, src/api/, tests/ y docs/trazabilidad_codigo.md.

**Nota de versión:** La evidencia de implementación se refiere al ZIP del repositorio revisado para esta versión del documento. Si el equipo modifica el código después de esa revisión, debe actualizarse esta matriz antes de entregar el PIA.
