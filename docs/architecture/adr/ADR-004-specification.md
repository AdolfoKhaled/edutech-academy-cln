# ADR-004: Specification Pattern para las reglas que se combinan

**Estado:** aceptado · **Fecha:** 2026-11-05

## Contexto
Varias reglas del negocio son condiciones que se combinan: la asistencia en línea se acredita con 60 % de conexión **o** con la grabación vista en 72 horas (INV-12); el criterio de certificación exige calificación mínima **y** asistencia mínima (INV-21); el paquete de datos del PIA pide evaluar si una solicitud puede procesarse (estudiante activo **y** con cursos **y** autorizada) y si aplica el beneficio por referencia (preferente **y** total ≥ 1500 **y no** promoción). El PIA exige Specification con AND, OR y NOT.

## Decisión
`src/domain/especificaciones.py` define `Specification` con `es_satisfecha_por()` e `incumplidas()`, y los operadores `&` (Conjuncion), `|` (Disyuncion) y `~` (Negacion). Las reglas compuestas son constantes con nombre: `PUEDE_PROCESARSE`, `BENEFICIO_REFERENCIA`, `ASISTENCIA_EN_LINEA` y `CriterioDeCertificacion.regla()`. `incumplidas()` devuelve qué condición falló, y ese texto llega al usuario en el mensaje de error.

## Alternativas
- **`if` dentro de cada método:** más corto, pero repite condiciones y no dice cuál falló.
- **Mantener solo Strategy (ADR-002):** sigue sirviendo para elegir el criterio Regular u Oficial; ahora cada criterio arma su regla con Specifications.

## Consecuencias
- Cada condición se prueba sola (`tests/unit/test_especificaciones.py`) y la regla compuesta se lee como el BRD.
- Las Specifications no modifican nada; la entidad decide y cambia su estado.
