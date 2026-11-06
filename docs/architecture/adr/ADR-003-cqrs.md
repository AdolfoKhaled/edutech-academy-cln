# ADR-003: CQRS para separar comandos y consultas de certificados

**Estado:** aceptado (el documento confirma la decisión) · **Fecha:** 2026-10-17

## Contexto
El caso CU-05 requiere una verificación pública sin registro ni credenciales que muestre únicamente nombre del titular, curso, fecha de conclusión y vigencia, sin datos de contacto ni calificaciones específicas. El documento señala que reutilizar el Aggregate `Certificado` o el repositorio general de escritura para esta consulta podría exponer información confidencial. El servicio público de consulta no necesita operaciones transaccionales como `guardar(certificado)`.

## Decisión
Mantener **CQRS**: utilizar `ICertificadoRepository` para la ejecución de comandos y un `CertificadoReadRepository` o Query Model dedicado para lectura. `VerificacionCertificadoAppService` delega la consulta al modelo de lectura, que devuelve solo los campos autorizados en el DTO de verificación pública.

## Alternativas
- **Usar el modelo de escritura o el Aggregate `Certificado` para consultar:** reutiliza componentes, pero puede cargar datos innecesarios y exponer información confidencial.
- **Separar lectura y escritura mediante CQRS (elegida):** requiere un repositorio o modelo de lectura y un DTO específico, pero limita los datos expuestos y optimiza las consultas.

## Consecuencias
- Beneficios: separación de responsabilidades, menor superficie de exposición de datos y consultas optimizadas.
- Costos: más componentes de lectura y escritura.
- Riesgos: si la proyección del modelo de lectura está mal definida, puede exponer datos que deben ocultarse; por ello debe probarse que el DTO no incluya contacto ni calificaciones.

## Trazabilidad
- Actividad Unidad 3, página 23: tabla de Queries, incluyendo `ConsultarCertificadoPublicoQuery` y su DTO.
- Página 15: decisión de que la regla de datos visibles vive en el modelo de lectura.
- Página 25: Etapa 7, apartado 4, Segregación de Interfaces (I), que confirma CQRS y la separación de `ICertificadoRepository` y la interfaz de lectura.
