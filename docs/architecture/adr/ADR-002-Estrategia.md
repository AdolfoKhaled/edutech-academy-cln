# ADR-002: Strategy para los criterios de certificación

**Estado:** aceptado (el documento registra el cambio como realizado) · **Fecha:** 2026-10-17

## Contexto
En la revisión SOLID, el criterio de certificación se modeló inicialmente como un Value Object estático dentro del Aggregate `Curso`, con dos valores fijos: Regular y Oficial. El Domain Service `ConsolidadorDeActa` cruza el expediente con esos valores para emitir un veredicto. Si se añade una política nueva, por ejemplo para clientes empresariales, habría que modificar el servicio con nuevos condicionales `if`/`switch`, incumpliendo el principio Abierto/Cerrado.

## Decisión
Transformar el Criterio de Certificación aplicando **Strategy**. Crear la interfaz `ICriterioCertificacion` con implementaciones concretas para que `ConsolidadorDeActa` evalúe cualquier política de forma polimórfica sin alterar su propio código fuente.

## Alternativas
- **Mantener condicionales en `ConsolidadorDeActa`:** simple al inicio, pero obliga a editar el servicio por cada nueva política.
- **Usar Strategy (elegida):** introduce una interfaz y sus implementaciones, pero permite agregar políticas mediante polimorfismo sin cambiar el código del consolidador.
- **Herencia `CursoPresencial`/`CursoEnLinea`:** no se adopta; el documento la descarta y mantiene `Modalidad` como Value Object.

## Consecuencias
- Beneficios: permite incorporar y probar nuevos criterios con menor impacto en el servicio central y cumple el principio Abierto/Cerrado.
- Costos: más interfaces e implementaciones que mantener.
- Riesgos: elegir la política incorrecta o duplicar reglas. Debe mantenerse coherencia con los criterios Regular y Oficial definidos en el dominio.

## Trazabilidad
- Actividad Unidad 3, páginas 24–25: Etapa 7, apartado 2, Principio de Abierto/Cerrado (O), donde se documenta el cambio realizado a `ICriterioCertificacion`.
- Página 15: decisión de modelar Criterio de Certificación como Value Object.
- Página 16: descarte de subclases `CursoPresencial` y `CursoEnLinea`.
