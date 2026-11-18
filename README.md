# R3DM TITAN — Multitareas Autopilot

**Estado: runtime local, catálogo de 81 tareas, planificador central y puentes preparados; conexiones comerciales reales y producción pendientes.**

Este repositorio es el negocio independiente **Multitareas Autopilot** dentro del ecosistema R3DM/TITAN. Mantiene código, configuración, datos, clientes, operaciones y cobros separados de QUASAR y de Superagente Multifunción. La reutilización entre proyectos se hace mediante adaptadores y contratos versionados, sin fusionar sus repositorios.

## Los tres Pulpos

- **ALPHA — Multitareas y servicios digitales:** intake, planificación, QA básico, registro estructural de fuentes y puntuación de oportunidades aportadas.
- **BETA — Marketplace y ventas:** clasificación de oportunidades, cualificación con consentimiento, conciliación aritmética de comisiones, cálculo de precio total y cálculo neto tras reservas.
- **GAMMA — Investigación tradicional:** validación estructural de datos, gate de exposición con entradas explícitas, separación de efectivo confirmado/pendiente y propuesta de capital tras reservas. Sin cripto y sin órdenes de inversión.

## Núcleo implementado

- Catálogo versionado de 81 tareas: ALPHA 37, BETA 29, GAMMA 15; tareas sin handler se detienen en NEEDS_ADAPTER.
- Seis handlers locales deterministas para fuentes, oportunidades, precios, reservas y capital.
- Planificador central asistido por IA que solo propone tareas del catálogo y nunca las ejecuta.
- Cola SQLite durable con reclamación atómica, idempotencia, auditoría, leases, recuperación y outbox.
- Runtime por lotes, scheduler opt-in y punto de entrada run_worker.py.
- Adaptador Ollama restringido a localhost; IA remota desactivada por defecto.
- Marketplace desactivado por defecto.
- Helper HMAC genérico y ledger idempotente de cobros entrantes en estado PENDING_RECONCILIATION.
- Puente HMAC preparado hacia Cerebro y cliente explícito de trabajos hacia Multifunción, ambos pendientes de conexión remota.
- CI de Python 3.11: 52 pruebas unitarias/integración local superadas en el último run verificado.

## Límites financieros

Los agentes no pueden gastar, comprar, contratar suscripciones, transferir, retirar, reembolsar ni ejecutar órdenes de inversión. GAMMA permanece RESEARCH_ONLY. Los cobros entrantes solo se registran tras verificar la firma específica del proveedor; la conciliación PSP/banco aún no está conectada. IVA, retenciones, comisiones, devoluciones, costes y beneficio neto deben permanecer separados.

## Ejecución local

Requiere Python 3.11 o posterior y solo usa la biblioteca estándar.

```sh
python run_worker.py --once
python run_worker.py
python -m unittest discover -s tests -v
```

La base SQLite se crea por defecto en data/multitareas.db. Configura MULTITAREAS_DATABASE para cambiar su ubicación. El scheduler no arranca al importar módulos. El dispatcher de Cerebro no envía nada sin CEREBRO_BASE_URL, CEREBRO_SHARED_SECRET y CEREBRO_EVENTS_PATH válidos.

## Estado de integración y producción

No está desplegado ni conectado a cuentas de marketplace, PSP, banco o broker. El puente Cerebro requiere confirmar el endpoint receptor real. El puente Multifunción requiere que la API objetivo de su PR #4 esté integrada y desplegada, además de URL y token de servicio. Las tareas sin handler quedan en NEEDS_ADAPTER; no se inventan datos ni se marca éxito por la mera existencia de una especificación. No activar producción hasta superar docs/production-gates.md.
