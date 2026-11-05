# ADR-006: Persistencia con SQLAlchemy Core, PostgreSQL y Unit of Work

**Estado:** aceptado (reemplaza la persistencia con sqlite3 de la Unidad 3) · **Fecha:** 2026-11-05

## Contexto
El PIA pide Docker Compose con una base de datos real y despliegue. En U3 la infraestructura usaba `sqlite3` directamente. Las pruebas deben seguir siendo rápidas.

## Decisión
`src/infrastructure/sql.py` usa SQLAlchemy Core. El motor se elige con `DATABASE_URL`: PostgreSQL en Docker, CI y producción; SQLite en memoria en las pruebas unitarias e integración. `SqlUnitOfWork` abre, confirma o revierte la transacción de cada caso de uso (`transaccion()` en `application/puertos.py`); fuera de una Unit of Work cada operación se confirma sola. Cada Aggregate se guarda serializado en `datos`, con columnas aparte para consultas y modelos de lectura (estado, saldo, folio, total). La restricción `UNIQUE` de `certificados.inscripcion` refuerza INV-25.

## Alternativas
- **ORM con mapeo completo de cada entidad:** más tablas y migraciones; no cabe en el plazo del PIA.
- **Seguir con sqlite3:** no permite usar PostgreSQL en Docker ni en producción.

## Consecuencias
- El dominio no cambió: los repositorios implementan las mismas interfaces de `domain/repositorios.py`.
- La misma prueba corre contra PostgreSQL cuando existe `TEST_DATABASE_URL` (CI y `docker compose run tests`).
- La serialización ata el formato guardado a las clases de Python; para producción real se migraría a columnas por atributo.
