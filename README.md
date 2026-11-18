# R3DM TITAN — Multitareas Autopilot

**Estado: runtime local y primera familia de bots integrados; conectores comerciales reales y producción pendientes.**

Este repositorio es el negocio independiente **Multitareas Autopilot** dentro del ecosistema R3DM/TITAN. Mantiene código, configuración, datos, clientes, operaciones y cobros separados de QUASAR y de Superagente Multifunción. La reutilización entre proyectos se hace mediante adaptadores y contratos versionados, sin fusionar sus repositorios.

## Objetivo

Automatizar de extremo a extremo las tareas comerciales y operativas permitidas, con supervisión, recuperación, trazabilidad y alertas. La meta operativa es que el titular solo compruebe que los cobros liquidados han llegado a su cuenta. Esto todavía requiere integrar y probar PSP/banco, webhooks específicos, conciliación y avisos fiables.

## Los tres Pulpos

- **ALPHA — Multitareas y servicios digitales:** intake, planificación de trabajos, QA de artefactos y futura ejecución/entrega mediante adaptadores autorizados.
- **BETA — Marketplace y ventas:** clasificación de oportunidades aportadas, cualificación con consentimiento y conciliación de comisiones. Los conectores de marketplace siguen desactivados.
- **GAMMA — Investigación tradicional:** validación de datos aportados, análisis de exposición cuando existen entradas explícitas y research sobre acciones, ETF, fondos, bonos, oro y materias primas. Sin cripto y sin órdenes de inversión.

## Núcleo implementado

- Cola SQLite durable con reclamación atómica, idempotencia y auditoría.
- Leases de worker, renovación y recuperación de tareas tras caída/expiración.
- Runtime por lotes, scheduler opt-in y punto de entrada run_worker.py.
- Registro de workers ALPHA/BETA/GAMMA y familias iniciales de bots.
- Adaptador Ollama restringido a localhost; IA remota desactivada por defecto.
- Adaptador marketplace desactivado por defecto.
- Helper HMAC genérico y ledger idempotente de cobros entrantes en estado PENDING_RECONCILIATION.
- CI de Python 3.11 con compilación y suite unitaria.

## Límites financieros

- Los agentes no pueden gastar, comprar, contratar suscripciones, transferir, retirar, reembolsar ni ejecutar órdenes de inversión.
- Los cobros entrantes solo se registran tras verificar la firma específica del proveedor; la conciliación PSP/banco aún no está conectada.
- IVA, retenciones, comisiones, devoluciones, costes y beneficio neto deben permanecer separados.
- No se inventan ventas, clientes, saldos ni cobros. No se guardan credenciales, secretos ni IBAN completos en Git.

## Ejecución local

Requiere Python 3.11 o posterior y solo usa la biblioteca estándar.

```sh
python run_worker.py --once
python run_worker.py
python -m unittest discover -s tests -v
```

La base SQLite se crea por defecto en data/multitareas.db. Configura MULTITAREAS_DATABASE para cambiar su ubicación. El scheduler no arranca al importar módulos: se inicia explícitamente mediante run_worker.py.

## Estado de producción

No está desplegado ni conectado a cuentas de marketplace, PSP, banco o broker. ALPHA y BETA generan planes/análisis y se detienen donde falta el adaptador autorizado; GAMMA es RESEARCH_ONLY. No activar producción hasta superar docs/production-gates.md.
