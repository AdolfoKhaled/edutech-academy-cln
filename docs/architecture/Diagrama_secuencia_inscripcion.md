# Diagrama de secuencia — Solicitud de inscripción y pago

**Alcance:** representa el flujo implementado de CU-01 en la API. El sistema contable se representa como actor externo que notifica el pago mediante el adaptador. La lista de espera es una rama alternativa cuando no hay cupo.

```mermaid
sequenceDiagram
    autonumber
    actor Estudiante
    participant API as API REST (FastAPI)
    participant Servicio as InscripcionService
    participant Grupo as Grupo (dominio)
    participant Inscripcion as Inscripcion (dominio)
    participant UoW as Unit of Work / Repositorios
    participant Contable as Sistema contable (adaptador)

    Estudiante->>API: POST /grupos/{grupoId}/inscripciones
    API->>Servicio: solicitarInscripcion(cmd)
    Servicio->>UoW: iniciar transacción y obtener Grupo/Curso
    Servicio->>Grupo: reservarLugar(inscripcionId)
    alt Hay cupo disponible
        Grupo-->>Servicio: lugar reservado + fecha límite
        Servicio->>Inscripcion: preinscribir(datos, costo, fecha límite)
        Servicio->>UoW: guardar Inscripción, Expediente y Grupo
        UoW-->>Servicio: commit
        Servicio-->>API: SolicitudRegistrada (Preinscrito)
        API-->>Estudiante: 201 — Inscripción Preinscrita
        Contable->>API: POST /inscripciones/{id}/pagos
        API->>Contable: pagoNotificado(id, monto, fecha)
        Contable->>Servicio: acreditarPago(id, monto, fecha)
        Servicio->>Inscripcion: registrarPago(PagoAcreditado)
        alt Pago acumulado >= 50%
            Inscripcion-->>Servicio: formalización + folio único
        else Pago menor a 50%
            Inscripcion-->>Servicio: abono; permanece Preinscrito
        end
        Servicio->>UoW: guardar Inscripción y commit
        API-->>Contable: estado actualizado + mensaje
    else Sin cupo
        Grupo->>Grupo: agregarAListaDeEspera(estudiante, fecha/hora)
        Servicio->>UoW: guardar Grupo y commit
        Servicio-->>API: EnListaDeEspera
        API-->>Estudiante: 202 — En lista de espera
    end
```

**Límites del diagrama:** no representa una integración bancaria real ni una notificación LMS; el repositorio modela el adaptador contable y expone la operación de pago. La formalización requiere las condiciones de negocio del dominio, incluido el pago acreditado.
