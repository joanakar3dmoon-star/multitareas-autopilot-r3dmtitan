# Phase 3 — bots, persistencia y conectores

## Bot families

- ALPHA: valida intake, crea un plan de trabajo y realiza QA básico de artefactos. Devuelve NEEDS_ADAPTER hasta configurar un adaptador autorizado de ejecución/entrega.
- BETA: clasifica oportunidades aportadas, cualifica leads solo con consentimiento explícito y concilia comisiones en unidades monetarias menores. No scrapea, no envía mensajes ni cursa pedidos.
- GAMMA: valida la estructura de datos, evalúa exposición solo con entradas explícitas y prepara research de activos tradicionales. Si faltan entradas de riesgo, informa NOT_EVALUATED. No afirma frescura de mercado. Rechaza cripto y nunca emite órdenes.

## Runtime

core/worker_registry.py registra los tres workers; core/app.py lo utiliza al construir el runtime. core/store.py proporciona cola SQLite, idempotencia, auditoría, leases, recuperación y outbox local. core/scheduler.py arranca únicamente desde run_worker.py.

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

CI ejecuta compilación y tests unitarios con Python 3.11. Los tests no sustituyen el handshake remoto, el sandbox del proveedor, la conciliación real ni las pruebas de caída/recuperación del despliegue.
