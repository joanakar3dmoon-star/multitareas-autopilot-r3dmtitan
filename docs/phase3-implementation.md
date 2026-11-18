# Phase 3 — bots, persistencia y conectores

## Catálogo y handlers

El catálogo versionado contiene 81 tareas (ALPHA 37, BETA 29, GAMMA 15). El runtime valida la combinación pulpo/bloque/tarea. Las tareas sin handler se detienen en NEEDS_ADAPTER; las tareas desconocidas quedan BLOCKED.

Hay 29 handlers locales deterministas:
- ALPHA: 4 handlers de inteligencia comercial más 13 tareas Upgrade distribuidas en oro físico spot, instrumentos vinculados, supply chain y diferenciales de mercado.
- BETA: cálculo de precio total, cálculo neto tras reservas, normalización de SKU, deduplicación, validación de precio/stock y cálculo de margen/comisión.
- GAMMA: separación de efectivo confirmado/pendiente, capital potencial tras reservas, identificación de instrumentos, riesgos de concentración/liquidez/FX, escenarios y spread/fees.

Los handlers Upgrade validan y calculan exclusivamente sobre datos suministrados; no descargan feeds, no verifican licencias/proveedores/certificados ni ejecutan compras. Las propuestas comerciales, precios, instrumentos y riesgos terminan en HUMAN_REVIEW cuando corresponde. GAMMA permanece RESEARCH_ONLY.

## Runtime

core/worker_registry.py registra workers y handlers; core/app.py construye el runtime. core/store.py proporciona cola SQLite, idempotencia, auditoría, leases, recuperación y outbox local. core/scheduler.py arranca únicamente desde run_worker.py.

## Bridges

- Cerebro: los cambios de estado generan un evento mínimo en outbox dentro de la transacción local. El dispatcher firma con HMAC-SHA256 y requiere URL, ruta de eventos y secreto configurados. No se envían payloads de trabajo ni datos personales. El roundtrip remoto no está verificado.
- Multifunción: cliente explícito para la API /api/pulpos/jobs de la PR #4 del repositorio superagente-autopilot-multifuncion. La PR objetivo está abierta y no prueba que exista un servicio desplegado. El cliente permanece desactivado por defecto y filtra campos sensibles. No hay reenvío automático.

## External adapters

- Ollama: HTTP local limitado a localhost, con timeout y límite de respuesta.
- Marketplaces: desactivados; requieren API oficial, scopes, términos y sandbox.
- Pagos: HMAC genérico y ledger idempotente; no es una integración de Stripe/Bizum/SEPA. El método de ledger recibe eventos que el llamante ya verificó; no verifica por sí mismo firmas específicas ni concilia con el banco.
- Banco: no implementado.
- Broker: no implementado; GAMMA sigue en research-only.

## Security

No existe capacidad para iniciar transferencias, payouts, reembolsos, compras, suscripciones ni órdenes de broker. Los recibos permanecen PENDING_RECONCILIATION. No guardar secretos, bodies completos de webhook ni datos personales innecesarios en Git o metadata.

## Validation

CI ejecuta compileall y 76 pruebas unitarias/integración local con Python 3.11. Los tests loopback no sustituyen el handshake remoto, el sandbox del proveedor, la conciliación real ni las pruebas de caída/recuperación del despliegue.
