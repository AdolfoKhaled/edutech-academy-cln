# Diagrama de componentes y despliegue — EduTech Academy

**Vista:** componentes lógicos y despliegue reproducible descrito por los archivos `Dockerfile`, `docker-compose.yml`, `render.yaml` y `src/`. Se muestran PostgreSQL/SQLite como opciones de persistencia configurables.

```mermaid
flowchart TB
    U[Estudiante / Instructor / Control Escolar / Coordinación] -->|HTTP + JSON| API[FastAPI\n src/api\n endpoints + DTO + OpenAPI]
    API --> APP[Aplicación\n src/application\n servicios + casos de uso + puertos]
    APP --> DOM[Dominio\n src/domain\n entidades + reglas + especificaciones + eventos]
    APP --> INFRA[Infraestructura\n src/infrastructure\n SQLAlchemy + repositorios + Unit of Work + adapters]
    INFRA --> DB[(PostgreSQL\n despliegue / Docker Compose)]
    INFRA -. configuración alternativa .-> SQLITE[(SQLite\n pruebas / desarrollo)]
    CSV[Paquete de datos CSV\n datos/] --> INFRA
    CONT[ Sistema contable externo ] -. notificación de pago vía adapter .-> INFRA
    LMS[ LMS / videoconferencia ] -. integración real no acreditada .-> APP

    subgraph Contenedor de aplicación
      API
      APP
      DOM
      INFRA
    end
```

## Despliegue contemplado

```mermaid
flowchart LR
    G[Repositorio GitHub] --> CI[GitHub Actions\n lint + pruebas + build] --> IMG[Imagen Docker]
    IMG --> R[Render Web Service]
    R --> PG[(Render PostgreSQL)]
    DEV[Entorno local] --> DC[Docker Compose] --> PGLOCAL[(PostgreSQL 16)]
    DC --> APPLOCAL[Contenedor FastAPI :8000]
    PGLOCAL --> APPLOCAL
```

## Responsabilidades y límites

- **API:** traduce solicitudes HTTP a operaciones de aplicación y publica OpenAPI/Swagger.
- **Aplicación:** coordina casos de uso, transacciones y puertos; no concentra las reglas centrales del negocio.
- **Dominio:** contiene entidades, objetos de valor, invariantes, especificaciones y eventos.
- **Infraestructura:** implementa persistencia, carga CSV y adaptadores externos.
- **Persistencia:** PostgreSQL se usa en Docker/Render según configuración; SQLite está contemplado para pruebas y desarrollo.
- **Integraciones externas:** el código incluye un adaptador contable simulado/modelado; no se debe afirmar que existe conexión real con un proveedor contable o LMS.

**Nota:** Render aparece configurado en el repositorio; la existencia de `render.yaml` no demuestra por sí sola que el despliegue esté activo o saludable.
