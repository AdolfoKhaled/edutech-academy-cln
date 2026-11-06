# ADR-001: Domain Model como patrón principal de lógica de negocio

**Estado:** aceptado (en la propuesta de arquitectura) · **Fecha:** 2026-10-17

## Contexto
En la Etapa 2, el sistema requiere reglas de negocio que cambian según el tipo de certificación y que relacionan varios conceptos. Para certificar, el curso regular exige mínimo 70/100 y 80 % de asistencia; el curso con certificación oficial exige 80/100 y 90 %. También hay transiciones críticas de inscripción, liberación de cupos y bloqueo de edición de actas cerradas. Se necesita centralizar reglas e invariantes y facilitar cambios futuros en las políticas.

## Decisión
Usar **Domain Model** como patrón principal. Las entidades y agregados controlan sus transiciones e invariantes; las reglas que varían, como los criterios de certificación, se representan de forma que puedan evolucionar sin reescribir los flujos de aplicación.

## Alternativas
- **Transaction Script:** duplica lógica en múltiples scripts y obliga a reescribir flujos cuando cambian las reglas.
- **Table Module:** agrupa lógica por tabla, pero se complica cuando las reglas abarcan varias entidades.
- **Domain Model (elegida):** encapsula reglas en entidades, usa estrategias y polimorfismo, protege estados e invariantes y permite cambios de negocio sin afectar directamente la persistencia; exige más diseño inicial y una curva de aprendizaje mayor.

## Consecuencias
- Beneficios: mayor cohesión, código testeable y representación fiel del negocio; reglas centralizadas para reducir errores operativos.
- Costos: inversión inicial de modelado y curva de aprendizaje.
- Riesgos: diseño incorrecto de límites de agregados o complejidad excesiva. La arquitectura debe conservar la separación entre dominio y persistencia.

## Trazabilidad
- Actividad Unidad 3, página 4: Etapa 2, tabla comparativa entre Transaction Script, Table Module y Domain Model.
- Reglas de negocio relacionadas: CU-04 y transiciones de estado identificadas en el mapa de dominio.
