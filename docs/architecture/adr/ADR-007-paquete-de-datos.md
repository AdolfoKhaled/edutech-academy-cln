# ADR-007: Adaptación del paquete de datos del profesor al dominio de EduTech

**Estado:** aceptado · **Fecha:** 2026-11-05

## Contexto
El paquete `15_EduTech_Academy` trae datos ficticios (actores, catálogo, operaciones, 120 casos y 20 transiciones) con un flujo de referencia SOLICITADA → ACEPTADA → INSCRITA → FINALIZADA / CANCELADA. El propio paquete aclara que no es un requerimiento y que debe adaptarse a los requerimientos del equipo.

## Decisión
Se agrega el Aggregate `SolicitudDeInscripcion` (un estudiante pide lugares en uno o varios cursos) y la carga pasa por las reglas de EduTech. Ver `docs/architecture/mapeo_datos_profesor.md`.

| Paquete | EduTech |
|---|---|
| SOLICITADA | Preinscrito |
| ACEPTADA + INSCRITA | Inscrito (en EduTech se formaliza en un paso, INV-06/07) |
| FINALIZADA | Concluido |
| CANCELADA | Liberada (US-06) |
| capacidad_o_stock | Cupo del grupo, ajustado a INV-03 (máximo 40 en línea) |

## Consecuencias
- 4 cursos del catálogo (43–52 lugares) quedan con cupo 40 y se informa en la carga.
- La regla `beneficio_referencia` se implementa como evaluación (elegible / no elegible); el BRD de EduTech no define un porcentaje, así que no cambia el importe. Pendiente de validar con el cliente.
- Los resultados de los 120 casos y 20 transiciones se generan con `scripts/ejecutar_casos.py` en `evidencias/`.
