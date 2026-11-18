# Arquitectura funcional

## Modelo de ejecución
Cada trabajo tiene identificador único, Pulpo propietario, vertical, origen, permisos, estado, eventos, artefactos y evidencia. Flujo común:

DISCOVERED → POLICY_CHECK → QUALIFIED → PLANNED → AUTHORIZED → RUNNING → QA → READY → SETTLED → CLOSED.

Estados alternativos: BLOCKED, FAILED, HUMAN_REVIEW, REFUND_PENDING y CANCELLED. No se permite saltar controles por un resultado de IA.

## ALPHA — Multitareas
Familias: captación de encargos, análisis de requisitos, planificación, navegador/automatización, desarrollo web, diseño, contenido, datos, QA, entrega, soporte y mantenimiento. Cada worker opera con permisos mínimos y adaptadores por plataforma. Las acciones externas se ejecutan solo con API oficial, OAuth o autorización compatible con las condiciones del servicio.

## BETA — Marketplace y afiliación
Familias: cazador de oportunidades, clasificador de ofertas, comparador de precios/condiciones, detector de fraude, captador de leads con base legítima, cualificador, agenda, vendedor asistido, CRM, atribución, conciliación de comisiones y postventa. El circuito termina en comisión verificada, no en una venta supuesta. No automatizar scraping prohibido, spam, cuentas falsas ni evasión de pagos de plataforma.

## GAMMA — Autoinversión tradicional
Familias: recolector de datos, investigación fundamental, análisis cuantitativo, macro, cartera, asignación, riesgo, cumplimiento, alertas, reconciliación y aprendizaje. Activos tradicionales únicamente; excluidos criptoactivos. El modo inicial es RESEARCH_ONLY. La ejecución real se bloquea hasta identificar broker, instrumentos permitidos, límites, custodia, comisiones, fiscalidad, autorizaciones y mecanismo de emergencia. Ningún worker puede transferir dinero ni elevar límites.

## Cerebro
Responsabilidades: memoria operativa versionada, políticas, selección de worker, planificación, coordinación, evaluación, registro de evidencia y recuperación. Los modelos generan propuestas; el motor determinista aplica permisos, límites y transiciones. El cerebro no puede otorgarse permisos a sí mismo.

## Ciclos
- Ciclo de tarea: eventos y reintentos acotados, idempotencia y dead-letter.
- Ciclo operativo: salud de workers, colas, latidos, bloqueos y alertas.
- Ciclo de negocio: conversión, margen, calidad, comisiones y retención.
- Ciclo de riesgo: límites, exposición, fraude, fallos de proveedor y parada segura.
- Ciclo de aprendizaje: métricas verificadas y feedback aprobado; no reentrenamiento implícito ni cambios autónomos de políticas.
