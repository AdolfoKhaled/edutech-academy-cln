# ADR-008: Contenedores, configuración por entorno (12-Factor) y despliegue en Render

**Estado:** aceptado · **Fecha:** 2026-11-05

## Contexto
El PIA pide Docker Compose para DB + App + Tests, variables de entorno y despliegue con Swagger activo.

## Decisión
- Una sola imagen (`Dockerfile`, Python 3.12) para la app y las pruebas; el puerto viene de `PORT`.
- `docker-compose.yml`: `db` (PostgreSQL 16), `app` (API) y `tests` (perfil `tests`, pytest contra PostgreSQL).
- Toda la configuración sale de variables (`src/config.py`): `DATABASE_URL`, `APP_ENV`, `CARGAR_DATOS_DEMO`, `ROLES_DEMO`. `.env.example` las documenta sin secretos.
- Despliegue en Render con `render.yaml` (servicio web Docker + PostgreSQL gratuito). La app carga los datos de demostración si la base está vacía.
- GitHub Actions: lint, pruebas con cobertura ≥ 80 % en SQLite y PostgreSQL, build y prueba con Docker Compose, y despliegue al hacer push a `main`.

## Alternativas
Railway o Fly.io (equivalentes; Render se eligió por el Blueprint en un archivo y el plan gratuito con PostgreSQL).

## Consecuencias
- El mismo código corre igual en local, en Docker y en producción; solo cambian las variables.
- La base gratuita de Render expira a los 30 días: suficiente para la defensa del PIA.
