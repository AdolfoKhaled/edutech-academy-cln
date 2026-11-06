**Proyecto:** Plataforma de gestión académica y certificación de EduTech Academy

**Curso:** Componentes de Lógica de Negocios

**Institución:** FIME – UANL

## Propósito

Este glosario establece un lenguaje común para los conceptos del negocio EduTech Academy. Las definiciones se basan en el BRD, las User Stories de la Unidad 2 y las precisiones del reporte de arquitectura de la Unidad 3.

**Criterio de alcance:** los términos describen el dominio completo del negocio. Que un término aparezca aquí no significa que la capacidad correspondiente esté implementada en los cinco casos de uso seleccionados en U3.

## Términos del dominio

| **Término**                       | **Definición**                                                                                                                                                                                                                                       |
|-----------------------------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Acta                              | Registro académico que consolida, por estudiante, la calificación final, el porcentaje de asistencia y el resultado frente al criterio de certificación del curso.                                                                                   |
| Acta Abierta                      | Estado del acta durante el cual puede prepararse la consolidación académica y todavía no se ha formalizado su cierre.                                                                                                                                |
| Acta Cerrada                      | Estado definitivo del acta después de validar el plazo y que no existan sesiones sin asistencia capturada. U3 establece que no debe modificarse; una corrección requeriría autorización formal de Coordinación Académica.                            |
| Administración                    | Área responsable de gestionar pagos, autorizar prórrogas y sobrecupos, y decidir compensaciones cuando se cancela un curso.                                                                                                                          |
| Asistencia                        | Registro de la participación de un estudiante en una sesión del curso. Se utiliza para calcular el porcentaje de asistencia.                                                                                                                         |
| Asistencia en línea               | Asistencia acreditada cuando el participante permanece conectado al menos 60% de la sesión en vivo o visualiza la grabación dentro de las 72 horas siguientes.                                                                                       |
| Calificación                      | Valor numérico asignado a una evaluación. La escala válida es de 0 a 100.                                                                                                                                                                            |
| Calificación Final                | Resultado calculado a partir de los promedios de evaluaciones parciales, proyecto y actividades, aplicando la ponderación registrada en el Curso.                                                                                                    |
| Cambio de Grupo                   | Solicitud para trasladar una inscripción a otro grupo del mismo curso y periodo. El BRD permite solicitarlo hasta 30% de avance; U3 añade un solo cambio por inscripción y disponibilidad en el grupo destino. No forma parte de los cinco CU de U3. |
| Certificado                       | Documento que acredita la conclusión satisfactoria de un programa. Contiene un folio único y datos asociados al estudiante, curso y fecha de conclusión.                                                                                             |
| Certificado Oficial               | Certificado asociado a un curso con criterio de certificación oficial: calificación mínima de 80/100 y asistencia mínima de 90%.                                                                                                                     |
| Código QR                         | Código que permite acceder a la consulta pública de autenticidad de un certificado.                                                                                                                                                                  |
| Cliente Empresarial               | Organización que contrata capacitación para sus participantes mediante un convenio y recibe reportes de avance y resultados.                                                                                                                         |
| Coordinación Académica            | Rol que aprueba programas, define ponderaciones y criterios, autoriza la emisión de certificados y gestiona decisiones académicas como sustituciones.                                                                                                |
| Control Escolar                   | Área que administra justificaciones, correcciones extemporáneas autorizadas, revisión de expedientes y consolidación del desempeño académico.                                                                                                        |
| Criterio de Certificación         | Condición académica que combina una calificación mínima y un porcentaje mínimo de asistencia para determinar si el estudiante cumple los requisitos del curso.                                                                                       |
| Criterio de Certificación Regular | Requiere calificación mínima de 70/100 y asistencia mínima de 80%.                                                                                                                                                                                   |
| Criterio de Certificación Oficial | Requiere calificación mínima de 80/100 y asistencia mínima de 90%.                                                                                                                                                                                   |
| Curso                             | Programa de capacitación ofrecido por EduTech Academy. Define modalidad, costo, ponderación y criterio de certificación.                                                                                                                             |
| Estudiante / Participante         | Persona que solicita inscripción, realiza pagos, asiste a sesiones y presenta evaluaciones para completar un curso.                                                                                                                                  |
| Expediente Académico              | Registro asociado a una inscripción que reúne asistencias, justificaciones y evaluaciones. De él se derivan la calificación final y el porcentaje de asistencia.                                                                                     |
| Examen de Recuperación            | Evaluación extraordinaria prevista para cursos regulares cuando el estudiante obtiene entre 60 y 69 puntos y cumple al menos 80% de asistencia. No forma parte de los cinco CU de U3.                                                                |
| Fecha Límite de Pago              | Fecha hasta la cual el estudiante debe regularizar el pago pendiente para conservar su lugar. La regla general de U2 establece siete días naturales desde el inicio del curso, con posibilidad de prórroga autorizada.                               |
| Folio de Certificado              | Identificador único asignado al certificado para consultarlo y verificar su autenticidad.                                                                                                                                                            |
| Folio de Inscripción              | Identificador único generado cuando una inscripción pasa al estado Inscrito.                                                                                                                                                                         |
| Grupo                             | Conjunto de estudiantes inscritos en una edición específica de un curso, con modalidad, cupo, calendario e instructor asignado.                                                                                                                      |
| Instructor                        | Rol académico responsable de impartir el curso, registrar asistencia dentro de 48 horas y capturar evaluaciones.                                                                                                                                     |
| Instructor Sustituto              | Instructor que asume un curso en sustitución de otro. No puede modificar evaluaciones capturadas por su predecesor; debe solicitar correcciones a Control Escolar.                                                                                   |
| Inscripción                       | Registro de la solicitud de un estudiante para participar en un grupo. Su estado puede ser Preinscrito, Inscrito o Liberada en el modelo de U3.                                                                                                      |
| Inscripción Inscrita              | Inscripción formalizada después de cumplir los requisitos de datos, cupo y pago acreditado según las reglas del negocio.                                                                                                                             |
| Lista de Espera                   | Relación ordenada por fecha y hora de estudiantes que esperan un lugar en un grupo lleno. Cuando se libera un lugar, se ofrece al primero durante 24 horas.                                                                                          |
| Modalidad                         | Forma en que se imparte un curso: presencial o en línea.                                                                                                                                                                                             |
| Ponderación                       | Distribución porcentual del valor de las evaluaciones parciales, proyecto final y actividades. El esquema estándar es 40%, 40% y 20%, respectivamente, y la suma debe ser 100%.                                                                      |
| Preinscrito                       | Estado de una inscripción registrada con datos completos y lugar reservado, pero que aún no alcanza el pago requerido para formalizarse. Puede realizar abonos y consultar el plazo de pago.                                                         |
| Porcentaje de Asistencia          | Proporción de sesiones acreditadas por el estudiante respecto al total de sesiones del curso, considerando las justificaciones válidas conforme a las reglas.                                                                                        |
| Portal de Validación Pública      | Módulo sin autenticación que permite consultar un certificado mediante folio o QR. Debe mostrar titular, curso, fecha de conclusión y vigencia/estatus, sin contacto ni calificaciones.                                                              |
| Recursamiento                     | Opción para volver a cursar un programa no acreditado dentro de los seis meses posteriores, con un descuento de 50%. No forma parte de los cinco CU de U3.                                                                                           |
| Solicitud de Inscripción          | Petición inicial del estudiante para incorporarse a un grupo. Si hay cupo y datos completos, puede registrarse como Preinscrito; si no hay cupo, se utiliza la lista de espera.                                                                      |
| Sobrecupo                         | Capacidad adicional de hasta 10% sobre el cupo máximo, sujeta a autorización de Administración. U3 registra una discrepancia sobre si aplica solo a modalidad en línea.                                                                              |
| Sistema Contable                  | Sistema externo que informa la acreditación de pagos. La plataforma depende de esa notificación para formalizar inscripciones.                                                                                                                       |
| Tercero / Empleador               | Persona u organización externa que consulta la autenticidad de un certificado sin depender de una respuesta manual de EduTech Academy.                                                                                                               |
| Vigencia del Certificado          | Estado que indica si un certificado se considera vigente. El BRD y las User Stories no especifican duración ni reglas de expiración; este concepto requiere definición del stakeholder.                                                              |

## Estados y transiciones relevantes

| **Estado**   | **Significado**                                                                                                                                                                                                |
|--------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Preinscrito  | Solicitud registrada, con pago pendiente y sin formalización académica definitiva.                                                                                                                             |
| Inscrito     | Inscripción formalizada al acreditarse el pago total o al menos la primera parcialidad del 50%, según U3.                                                                                                      |
| Liberada     | Estado propuesto por el equipo de U3 para representar la liberación del lugar después del vencimiento del pago. El reporte advierte que U2 habla de liberar el lugar, pero no define expresamente este estado. |
| Acta Abierta | Acta que todavía no ha sido cerrada formalmente.                                                                                                                                                               |
| Acta Cerrada | Acta consolidada y bloqueada para modificaciones ordinarias.                                                                                                                                                   |

## Reglas de consistencia terminológica

1.  Utilizar **Estudiante** o **Participante** para la persona que toma el curso; conservar **Cliente Empresarial** para la organización que contrata la capacitación.

2.  Utilizar **Inscripción** para el registro individual y **Grupo** para la edición del curso.

3.  No utilizar **Preinscrito** e **Inscrito** como sinónimos: representan estados distintos.

4.  Distinguir **Criterio Regular** de **Criterio Oficial**; no intercambiar sus mínimos.

5.  Utilizar **Acta** para el consolidado académico y **Certificado** para el documento que acredita el cumplimiento.

6.  Diferenciar **emisión** del certificado (generación y autorización) de **publicación** (disponibilidad para consulta).

7.  No asignar una duración a la **Vigencia del Certificado** hasta que el stakeholder la defina.

8.  No presentar **Cambio de Grupo**, **Cancelación**, **Recursamiento**, **Examen de Recuperación** o **Capacitación Empresarial** como implementados solo porque aparecen en el glosario o BRD: no están cubiertos por los cinco CU de U3.

9.  La tolerancia de dos sesiones y el plazo de siete días naturales son dos expresiones presentes en los documentos. No deben fusionarse en una sola regla hasta que se aclare su relación.

10. El sobrecupo tiene una discrepancia entre el BRD de U2 y el guion resumido en U3; mantenerla identificada hasta que el equipo la resuelva.

## Fuentes internas

- Glosario EduTech Academy, Unidad 2, 10/09/2026.

- BRD EduTech Academy, Unidad 2, 10/09/2026.

- User Stories EduTech Academy, Unidad 2, 10/09/2026 (US-01 a US-20).

- Reporte de arquitectura del sistema EduTech Academy, Unidad 3: mapa de dominio, fichas de invariantes INV-01 a INV-25 y decisiones dudosas.

- Repositorio edutech-academy-cln, consultado para distinguir los términos del dominio de las capacidades implementadas.
