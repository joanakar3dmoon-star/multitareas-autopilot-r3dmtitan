# R3DM TITAN — Multitareas Autopilot

**Estado: runtime local, bots iniciales y puentes preparados; conexiones externas reales y producción pendientes.**

Este repositorio es el negocio independiente **Multitareas Autopilot** dentro del ecosistema R3DM/TITAN. Mantiene código, configuración, datos, clientes, operaciones y cobros separados de QUASAR y de Superagente Multifunción. La reutilización entre proyectos se hace mediante adaptadores y contratos versionados, sin fusionar sus repositorios.

## Los tres Pulpos

- **ALPHA — Multitareas y servicios digitales:** intake, planificación de trabajos, QA de artefactos y futura ejecución/entrega mediante adaptadores autorizados.
- **BETA — Marketplace y ventas:** clasificación de oportunidades aportadas, cualificación con consentimiento y conciliación de comisiones. Los conectores de marketplace siguen desactivados.
- **GAMMA — Investigación tradicional:** validación estructural de datos aportados, análisis de exposición solo con entradas explícitas y research sobre acciones, ETF, fondos, bonos, oro y materias primas. Sin cripto y sin órdenes de inversión.

## Núcleo implementado

- Cola SQLite durable con reclamación atómica, idempotencia, auditoría, leases y recuperación.
- Runtime por lotes, scheduler opt-in y punto de entrada run_worker.py.
- Registro de workers ALPHA/BETA/GAMMA y familias iniciales de bots.
- Adaptador Ollama restringido a localhost; IA remota desactivada por defecto.
- Adaptador marketplace desactivado por defecto.
- Helper HMAC genérico y ledger idempotente de cobros entrantes en estado PENDING_RECONCILIATION.
- Outbox local que genera eventos mínimos de estado y puente HMAC preparado hacia Cerebro.
- Cliente explícito de trabajos hacia Superagente Multifunción, desactivado por defecto y basado en su API /api/pulpos/jobs de la PR #4 pendiente de despliegue.
- CI de Python 3.11 con compilación y suite unitaria.

## Límites financieros

Los agentes no pueden gastar, comprar, contratar suscripciones, transferir, retirar, reembolsar ni ejecutar órdenes de inversión. Los cobros entrantes solo se registran tras verificar la firma específica del proveedor; la conciliación PSP/banco aún no está conectada. IVA, retenciones, comisiones, devoluciones, costes y beneficio neto deben permanecer separados.

## Ejecución local

Requiere Python 3.11 o posterior y solo usa la biblioteca estándar.

```sh
python run_worker.py --once
python run_worker.py
python -m unittest discover -s tests -v
```

La base SQLite se crea por defecto en data/multitareas.db. Configura MULTITAREAS_DATABASE para cambiar su ubicación. El scheduler no arranca al importar módulos: se inicia explícitamente mediante run_worker.py. El dispatcher de Cerebro no envía nada sin CEREBRO_BASE_URL, CEREBRO_SHARED_SECRET y CEREBRO_EVENTS_PATH válidos.

## Estado de integración y producción

No está desplegado ni conectado a cuentas de marketplace, PSP, banco o broker. El puente Cerebro requiere confirmar el endpoint receptor real. El puente Multifunción requiere que la API objetivo de su PR #4 esté integrada y desplegada, además de URL y token de servicio. ALPHA y BETA generan planes/análisis y se detienen donde falta el adaptador autorizado; GAMMA es RESEARCH_ONLY. No activar producción hasta superar docs/production-gates.md.
