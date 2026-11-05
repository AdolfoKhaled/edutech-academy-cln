# ADR-005: API REST con FastAPI y contrato de errores

**Estado:** aceptado · **Fecha:** 2026-11-05

## Contexto
El PIA pide una API REST documentada con Swagger/OpenAPI activo en producción. Las reglas ya viven en el dominio y en los servicios de aplicación.

## Decisión
`src/api/main.py` usa FastAPI. Cada endpoint convierte la petición en un Command o llamada al servicio y el resultado en un DTO (`src/api/esquemas.py`); no contiene reglas. Las excepciones del dominio se traducen en un solo lugar:

| Código | Cuándo | Excepciones |
|---|---|---|
| 200 / 201 | Éxito / recurso creado | — |
| 202 | Grupo lleno: queda en lista de espera | `EnListaDeEspera` |
| 400 | Petición mal formada (falta un dato o tipo inválido) | `RequestValidationError` |
| 403 | El usuario no tiene el rol | `AccesoDenegado`, `CertificadoNoAutorizado`, `EvaluacionDeOtroInstructor` |
| 404 | No existe | `NoEncontrado` |
| 409 | La máquina de estados o el momento no lo permiten, o dato único duplicado | `TransicionNoPermitida`, `ActaYaCerrada`, `EdicionBloqueada`, `IntegrityError` |
| 422 | Regla de negocio incumplida | resto de `ErrorDeDominio` |

Los errores responden solo `{"mensaje": "..."}` en español. El usuario se indica con el encabezado `X-Usuario` (la autenticación es externa, D-06). Las fechas del negocio (`ahora`, `hoy`) son opcionales en el cuerpo para poder demostrar plazos.

## Alternativas
Flask + flasgger (más código para OpenAPI); Django REST (más pesado para el alcance).

## Consecuencias
- OpenAPI se genera del código: `docs/api/openapi.json` (`python scripts/exportar_openapi.py`) y `/docs` en vivo.
- Las peticiones se atienden de una en una (un candado alrededor de la conexión compartida); suficiente para la demostración, no para alta concurrencia.
