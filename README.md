# EduTech Academy · Componentes de Lógica de Negocio (PIA)

Sistema de inscripciones, asistencia, calificaciones, actas y certificados de **EduTech Academy**, construido a partir del BRD, las User Stories/Gherkin y el diseño DDD de las Unidades 2 y 3. Implementa DDD, Specification Pattern, máquina de estados, Domain Events y una API REST documentada con OpenAPI.

**Equipo:** Adolfo Khaled Mendoza Cervantes · Eros Vargas Mariscal · Jesús Enrique García Mendoza · Kevin Armando Vargas Briones
**Curso:** Componentes de Lógica de Negocio · FIME, UANL · Profesor Miguel Ángel Gómez Marroquín

- Repositorio: https://github.com/AdolfoKhaled/edutech-academy-cln
- Panel para el usuario: https://edutech-academy-api.onrender.com/panel
- API documentada (Swagger): https://edutech-academy-api.onrender.com/docs

## Estructura

```
docs/
  BRD.md                     BRD, User Stories/Gherkin, BPMN y glosario (equipo de análisis)
  architecture/              ADRs, diagramas DDD/UML, mapeo del paquete de datos
  api/openapi.json           especificación OpenAPI exportada del código
  trazabilidad_codigo.md     regla → componente → endpoint → prueba
src/
  domain/                    Aggregates (Grupo, Inscripción, SolicitudDeInscripción, Expediente, Acta, Certificado),
                             Value Objects, Specifications, eventos, errores e interfaces de repositorio
  application/               servicios de aplicación (casos de uso CU-01 a CU-05), Commands y puertos
  infrastructure/            SQLAlchemy (PostgreSQL/SQLite), Unit of Work, adapters y carga de los CSV
  api/                       FastAPI: endpoints, DTOs, mensajes de error en español y panel web (panel.html)
  config.py · sistema.py     configuración por variables de entorno y composition root
tests/unit · tests/integration   332 pruebas (una corre solo con PostgreSQL) · cobertura 99 %
datos/                       paquete de datos ficticios del profesor (sin cambios)
scripts/                     casos del paquete y exportación de OpenAPI
evidencias/                  resultados de los 120 casos y 20 transiciones
.github/workflows/ci.yml     CI/CD   ·   Dockerfile · docker-compose.yml · render.yaml · .env.example
```

La dependencia va hacia adentro: `api → application → domain`, e `infrastructure` implementa las interfaces del dominio y la aplicación. El dominio no importa FastAPI ni SQLAlchemy.

## Ejecutar en local (sin Docker)

Requiere Python 3.11 o superior.

```bash
python -m venv .venv
# Windows: .\.venv\Scripts\Activate.ps1      macOS/Linux: source .venv/bin/activate
python -m pip install -r requirements-dev.txt
copy .env.example .env                 # macOS/Linux: cp .env.example .env
uvicorn src.api.main:app --reload      # http://127.0.0.1:8000/docs
```

Con la configuración por defecto usa SQLite (`edutech.db`) y al arrancar carga los datos del paquete (40 estudiantes, 20 cursos, 60 solicitudes).

## Ejecutar con Docker Compose (DB + App + Tests)

```bash
docker compose up --build db app                 # PostgreSQL + API en http://localhost:8000/docs
docker compose --profile tests run --rm tests    # pruebas contra PostgreSQL con cobertura
docker compose down -v                           # apagar y borrar la base
```

## Pruebas y calidad

```bash
python -m ruff check src tests scripts
python -m pytest -v --cov=src --cov-report=term-missing --cov-fail-under=80
python scripts/ejecutar_casos.py       # 120 casos + 20 transiciones del paquete -> evidencias/
python scripts/exportar_openapi.py     # docs/api/openapi.json
```

Las pruebas usan SQLite en memoria; si existe `TEST_DATABASE_URL`, también corren contra PostgreSQL. El pipeline de GitHub Actions ejecuta lint, pruebas en SQLite y PostgreSQL, los casos del paquete, el build con Docker Compose (DB + App + Tests) y el despliegue.

## Variables de entorno

| Variable | Para qué | Ejemplo |
|---|---|---|
| `DATABASE_URL` | Motor de base de datos | `postgresql+psycopg://usuario:clave@db:5432/edutech` |
| `APP_ENV` | Nombre del entorno | `produccion` |
| `CARGAR_DATOS_DEMO` | Cargar `datos/*.csv` si la base está vacía | `true` |
| `ROLES_DEMO` | Usuarios de demostración y sus roles | `inst-1:Instructor;coord-1:CoordinacionAcademica` |

## Despliegue en Render

1. En render.com: **New → Blueprint** y elegir este repositorio. `render.yaml` crea la base PostgreSQL y el servicio web con el `Dockerfile`.
2. Al terminar, abrir `https://<servicio>.onrender.com/docs`.
3. Opcional: copiar el *Deploy Hook* del servicio en el secreto `RENDER_DEPLOY_HOOK` del repositorio para que el pipeline despliegue al hacer push a `main`.

## Panel para el usuario (`/panel`)

Página web sencilla sobre la misma API, pensada para quien no conoce Swagger: lista de solicitudes con botones
**Revisar**, **Formalizar**, **Concluir** y **Cancelar**; alta de solicitudes; cursos con su cupo; inscripción a un
grupo con pago; y verificación pública de certificados. Cada acción muestra el mensaje de la API en verde (éxito) o
en rojo con su tipo: "Revisa los datos" (400), "Sin permiso" (403), "No encontrado" (404), "No se puede hacer en
este momento" (409) y "No cumple una regla del negocio" (422).

## Mensajes de la API

Todas las respuestas de error traen solo `{"mensaje": "..."}`, en español y sin términos técnicos:

| Código | Ejemplo de mensaje |
|---|---|
| 400 | El dato 'lugares' (curso 1) debe ser mayor o igual a 1. |
| 403 | El usuario ce-1 no tiene permiso para esta acción; se requiere el rol Instructor o plataforma LMS. |
| 404 | No existe la solicitud EDU-O999. |
| 409 | No se puede formalizar la solicitud EDU-O001 porque está en estado Inscrito. Solo se puede formalizar cuando está en Preinscrito. |
| 422 | No se puede formalizar la solicitud EDU-O033: el estudiante está dado de baja. |

## IDs para probar (datos del paquete del profesor)

| Qué | IDs | Resultado al formalizar |
|---|---|---|
| Solicitudes válidas | `EDU-O001`, `EDU-O002`, `EDU-O003` (42 en total) | 200 · Inscrito |
| Sin cursos | `EDU-O013`, `EDU-O039` | 422 · no tiene ningún curso |
| Estudiante dado de baja | `EDU-O033` a `EDU-O037` | 422 · el estudiante está dado de baja |
| Sin autorización | `EDU-O008`, `O016`, `O024`, `O032`, `O040`, `O048`, `O056` | 422 · no está autorizada |
| Curso deshabilitado (`EDU-P011`) | `EDU-O005`, `O015`, `O020`, `O055` | 422 · el curso no está disponible |
| Con promoción (sin beneficio) | `EDU-O009`, `O018`, `O027`, `O036`, `O045`, `O054` | Revisión: beneficio No |
| Estudiantes | `EDU-C001` … `EDU-C040` (dados de baja: `C007`, `C014`, `C021`, `C028`, `C035`) | — |
| Cursos y grupos | `EDU-P001` … `EDU-P020` · grupos `G-EDU-P001` … (`G-EDU-P001` tiene 13 lugares) | — |
| Usuarios (`X-Usuario`) | `inst-1`, `inst-2` Instructor · `ce-1` Control Escolar · `coord-1` Coordinación | — |
| No existen | `EDU-O999`, `NADA` | 404 |

## Guion de la demostración (Swagger, `/docs`)

Usuarios para el encabezado `X-Usuario`: `inst-1` (Instructor), `ce-1` (Control Escolar), `coord-1` (Coordinación Académica).

| Paso | Petición | Qué demuestra |
|---|---|---|
| 1 | `POST /demo/reiniciar` | Datos limpios; 4 cursos ajustados a cupo 40 (INV-03) |
| 2 | `GET /solicitudes/EDU-O001/evaluacion` | Specifications AND/NOT: puede procesarse, beneficio |
| 3 | `POST /solicitudes/EDU-O001/formalizar` → 200 | Preinscrito → Inscrito, evento, folio, lugares reservados |
| 4 | Repetir el paso 3 → **409** | La máquina de estados no permite formalizar dos veces |
| 5 | `POST /solicitudes/EDU-O013/formalizar` → **422** | Sin cursos: la regla dice qué falta |
| 6 | `POST /solicitudes/EDU-O004/concluir` → **409** | No se salta de Preinscrito a Concluido |
| 7 | `GET /solicitudes/EDU-O999` → **404** | No existe |
| 8 | `POST /grupos/G-EDU-P001/inscripciones` → 201 | CU-01: Preinscrito con fecha límite de pago |
| 9 | `POST /inscripciones/{id}/pagos` con el 50 % | INV-06/07: queda Inscrito con folio |
| 10 | `POST /inscripciones/{id}/asistencias` con `X-Usuario: ce-1` → **403** | Autorización por rol (D-06) |
| 11 | Asistencia y evaluaciones con `inst-1`, `POST /grupos/G-EDU-P001/acta/cierre`, `POST /certificados` con `coord-1`, `GET /verificacion/{folio}` | CU-02 a CU-05 completos |

Los campos `ahora` y `hoy` del cuerpo permiten simular fechas (plazo de 48 h, 5 días hábiles para cerrar el acta). Ver `tests/integration/test_api.py::test_curso_completo_por_la_api` para las fechas exactas.
