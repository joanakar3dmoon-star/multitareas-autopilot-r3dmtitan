# R3DM TITAN — Multitareas Autopilot

**Estado: runtime local, API autenticada, catálogo de 81 tareas, 29 handlers iniciales, planificador central y puentes preparados; conexiones comerciales reales y producción pendientes.**

Este repositorio es el negocio independiente **Multitareas Autopilot** dentro del ecosistema R3DM/TITAN. Mantiene código, configuración, datos, clientes, operaciones y cobros separados de QUASAR y de Superagente Multifunción. La reutilización entre proyectos se hace mediante adaptadores y contratos versionados, sin fusionar sus repositorios.

## Los tres Pulpos

- **ALPHA — Multitareas y servicios digitales:** intake, planificación, QA básico, inteligencia comercial aportada y las cuatro familias Upgrade: oro físico spot, instrumentos vinculados, supply chain y diferenciales de mercado.
- **BETA — Marketplace y ventas:** clasificación de oportunidades, cualificación con consentimiento, conciliación aritmética de comisiones, cálculo de precios/márgenes/reservas y normalización/deduplicación de catálogo.
- **GAMMA — Investigación tradicional:** validación estructural, identificación de instrumentos, evaluación de concentración/liquidez/FX, escenarios aritméticos, separación de efectivo confirmado/pendiente y propuesta de capital tras reservas. Sin cripto y sin órdenes de inversión.

## Núcleo implementado

- Catálogo versionado de 81 tareas: ALPHA 37, BETA 29, GAMMA 15; tareas sin handler se detienen en NEEDS_ADAPTER.
- 29 handlers locales deterministas: ALPHA 17, BETA 6 y GAMMA 6.
- Planificador central asistido por IA que solo propone tareas del catálogo y nunca las ejecuta.
- API HTTP autenticada para encolar tareas, consultar estado, ver cobertura y pedir planes; worker thread integrado.
- Cola SQLite durable con reclamación atómica, idempotencia, auditoría, leases, recuperación y outbox.
- Adaptador Ollama restringido a localhost; IA remota desactivada por defecto.
- Marketplace desactivado por defecto.
- Helper HMAC genérico y ledger idempotente de cobros entrantes en estado PENDING_RECONCILIATION.
- Puente HMAC preparado hacia Cerebro y cliente explícito de trabajos hacia Multifunción, ambos pendientes de conexión remota.
- Dockerfile y CI con compileall, 83 pruebas unitarias/integración local y construcción de imagen sin publicar.

## Límites financieros

Los agentes no pueden gastar, comprar, contratar suscripciones, transferir, retirar, reembolsar ni ejecutar órdenes de inversión. GAMMA permanece RESEARCH_ONLY. Los cobros entrantes solo se registran tras verificar la firma específica del proveedor; la conciliación PSP/banco aún no está conectada. IVA, retenciones, comisiones, devoluciones, costes y beneficio neto deben permanecer separados.

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

## Estado de integración y producción

No está desplegado ni conectado a cuentas de marketplace, PSP, banco o broker. Los handlers Upgrade procesan datos aportados y no consultan feeds externos. El puente Cerebro requiere confirmar el endpoint receptor real. El puente Multifunción requiere que la API objetivo de su PR #4 esté integrada y desplegada, además de URL y token de servicio. Las tareas sin handler quedan en NEEDS_ADAPTER; no se inventan datos ni se marca éxito por la mera existencia de una especificación. No activar producción hasta superar docs/production-gates.md.
