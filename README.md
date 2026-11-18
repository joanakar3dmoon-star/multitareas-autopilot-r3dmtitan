# R3DM TITAN — Multitareas Autopilot

**Estado: runtime local, API autenticada, catálogo de 81 tareas, 29 handlers locales, planificador y puentes opt-in preparados; conexiones externas reales y producción pendientes.**

Este repositorio es el negocio independiente **Multitareas Autopilot** dentro del ecosistema R3DM/TITAN. Mantiene código, configuración, datos, clientes, operaciones y cobros separados de QUASAR y de Superagente Multifunción. La reutilización entre proyectos se hace mediante adaptadores y contratos versionados, sin fusionar sus repositorios.

## Los tres Pulpos

- **ALPHA — Multitareas y servicios digitales:** intake, planificación, QA básico, inteligencia comercial aportada y cuatro familias Upgrade.
- **BETA — Marketplace y ventas:** clasificación de oportunidades, cualificación con consentimiento, conciliación aritmética de comisiones, precios/márgenes/reservas y catálogo.
- **GAMMA — Investigación tradicional:** calidad de datos, instrumentos, concentración/liquidez/FX, escenarios y reserva de capital. Sin cripto, sin trading y sin órdenes.

## Núcleo implementado

- Catálogo versionado de 81 tareas: ALPHA 37, BETA 29, GAMMA 15; tareas sin handler se detienen en NEEDS_ADAPTER.
- 29 handlers locales deterministas: ALPHA 17, BETA 6 y GAMMA 6.
- Planificador central asistido por IA que solo propone tareas del catálogo y nunca las ejecuta.
- API HTTP autenticada para encolar tareas, consultar estado, ver cobertura y pedir planes; worker thread integrado.
- Cola SQLite durable con reclamación atómica, idempotencia, auditoría, leases, recuperación y outbox.
- Adaptador Ollama restringido a localhost; IA remota desactivada por defecto.
- Marketplace desactivado por defecto.
- Helper HMAC genérico y ledger idempotente de cobros entrantes en estado PENDING_RECONCILIATION.
- Fase 4: adaptador HMAC opt-in hacia el receptor de eventos Cerebro/QUASAR y cliente opt-in de jobs hacia Multifunción. Ambos desactivados por defecto, con tests de contrato y allowlists.
- Dockerfile y CI con compileall, 84 pruebas documentadas y construcción de imagen sin publicar.

## Límites financieros

Los agentes no pueden gastar, comprar, contratar suscripciones, transferir, retirar, reembolsar ni ejecutar órdenes de inversión. GAMMA permanece RESEARCH_ONLY. Los cobros entrantes solo se registran tras verificar la firma específica del proveedor; conciliación PSP/banco aún no conectada. IVA, retenciones, comisiones, devoluciones, costes y beneficio neto deben permanecer separados.

## Ejecución local

Requiere Python 3.11 o posterior y solo usa la biblioteca estándar.

```sh
export MULTITAREAS_API_TOKEN="$(openssl rand -hex 32)"
python run_server.py
```

- GET /health — health check básico.
- GET /api/coverage — requiere cabecera X-Multitareas-Token.
- POST /api/tasks — requiere token; crea una tarea y devuelve 202.
- GET /api/tasks/{task_id} — requiere token.
- POST /api/plans — requiere token; genera una propuesta, no la ejecuta.

La base SQLite se crea por defecto en data/multitareas.db. Configura MULTITAREAS_DATABASE para cambiar su ubicación. Para Docker, usa el volumen persistente /data y MULTITAREAS_DATABASE=/data/multitareas.db. El servicio combina API y worker en un proceso y debe operar con una sola réplica mientras use SQLite.

## Configuración de puentes — desactivados por defecto

Cerebro/QUASAR:
- MULTITAREAS_CEREBRO_BRIDGE_ENABLED=1
- CEREBRO_BASE_URL=https://<host>
- CEREBRO_SHARED_SECRET=<secreto aleatorio compartido de al menos 32 caracteres>
- Contrato: r3dm-cerebro-bridge-v1; emite solo task_id, pulpo, vertical y state.

Multifunción:
- MULTIFUNCION_BRIDGE_ENABLED=1
- MULTIFUNCION_BASE_URL=https://<host>
- MULTIFUNCION_API_TOKEN=<token de servicio independiente de al menos 32 caracteres>
- Ruta API prevista: POST /api/pulpos/jobs, con Idempotency-Key.

No actives ninguna variable todavía: QUASAR PR #123 y Multifunción PR #4 siguen pendientes de merge/despliegue. Los secretos deben configurarse únicamente en el gestor de secretos del hosting, nunca en Git ni en archivos de configuración.

## Estado de integración y producción

No está desplegado ni conectado a cuentas de marketplace, PSP, banco o broker. Los handlers Upgrade procesan datos aportados y no consultan feeds externos. El receptor Cerebro está propuesto en QUASAR PR #123; la API Multifunión está propuesta en su PR #4. Este repositorio incorpora el lado emisor/cliente, no una conexión LIVE demostrada. Las tareas sin handler quedan en NEEDS_ADAPTER; no se inventan datos ni se marca éxito por la mera existencia de una especificación. No activar producción hasta superar docs/production-gates.md.
