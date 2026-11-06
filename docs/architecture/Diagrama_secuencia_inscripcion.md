# Diagrama de secuencia — Solicitud de inscripción y pago

**Alcance:** representa el CU-01 implementado en la API: solicitud de inscripción, reserva de lugar o entrada a lista de espera y acreditación de pago. El sistema contable se modela como el origen externo de la notificación de pago; el adaptador incluido en el repositorio delega la operación a `InscripcionService`.

```mermaid
sequenceDiagram
    autonumber
    actor Estudiante
    participant API as API REST FastAPI
    participant Servicio as InscripcionService
    participant Grupo as Grupo dominio
    participant Inscripcion as Inscripcion dominio
    participant UoW as UnitOfWork y repositorios
    actor Contable as Sistema contable externo
    participant Adapter as SistemaContableAdapter

    Estudiante->>API: POST solicitud de inscripcion
    API->>Servicio: solicitarInscripcion cmd
    Servicio->>UoW: iniciar transaccion
    Servicio->>Grupo: reservarLugar inscripcionId

    alt Hay cupo disponible
        Grupo-->>Servicio: reserva y fechaLimitePago
        Servicio->>Inscripcion: preinscribir datos y costo
        Servicio->>UoW: guardar Inscripcion Expediente y Grupo
        Servicio->>UoW: confirmar transaccion
        Servicio-->>API: SolicitudRegistrada Preinscrito
        API-->>Estudiante: 201 Created estado Preinscrito
    else No hay cupo
        Servicio->>Grupo: agregarAListaDeEspera
        Servicio->>UoW: guardar Grupo y confirmar transaccion
        Servicio-->>API: EnListaDeEspera
        API-->>Estudiante: 202 Accepted lista de espera
    end

    opt Sistema contable acredita un pago
        Contable->>API: POST notificacion de pago
        API->>Adapter: pagoNotificado
        Adapter->>Servicio: acreditarPago
        Servicio->>UoW: iniciar transaccion
        Servicio->>Inscripcion: registrarPago

        alt Pago acumulado alcanza el 50 por ciento
            Inscripcion-->>Servicio: InscripcionFormalizada con folio
        else Pago acumulado menor al 50 por ciento
            Inscripcion-->>Servicio: abono registrado y estado Preinscrito
        end

        Servicio->>UoW: guardar Inscripcion y confirmar transaccion
        Servicio-->>Adapter: resultado de acreditacion
        Adapter-->>API: resultado de pago
        API-->>Contable: respuesta con estado de Inscripcion
    end
```

## Correspondencia con el repositorio

- `POST /grupos/{grupoId}/inscripciones`: `src/api/main.py`, operación `inscribir`.
- `InscripcionService.solicitarInscripcion`: `src/application/inscripcion_service.py`; reserva lugar, crea la preinscripción y registra la lista de espera cuando no hay cupo.
- `POST /inscripciones/{inscripcionId}/pagos`: `src/api/main.py`, operación `pagar`.
- `SistemaContableAdapter.pagoNotificado`: `src/infrastructure/adapters.py`; delega en `InscripcionService.acreditarPago`.
- `Inscripcion.registrarPago`: `src/domain/inscripcion.py`; determina si el pago acumulado formaliza la inscripción y genera el folio.

**Límite:** el repositorio contiene un adaptador que modela la notificación del sistema contable, pero no acredita una conexión real con un proveedor contable externo. El diagrama no representa una pasarela bancaria ni una integración real de terceros.
