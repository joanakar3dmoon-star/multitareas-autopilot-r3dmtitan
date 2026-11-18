# Phase 3 — bots, persistencia y conectores

## Bot families and catalog handlers

El catálogo versionado contiene 81 tareas (ALPHA 37, BETA 29, GAMMA 15). El runtime valida la combinación pulpo/bloque/tarea. Las tareas sin handler se detienen en NEEDS_ADAPTER; las tareas desconocidas quedan BLOCKED.

Hay 16 handlers locales deterministas registrados:
- ALPHA: record_sources, score_opportunity, identify_customer_pain y compare_commissions.
- BETA: calculate_total_price, calculate_net_after_reserves, normalize_skus_variants_categories, deduplicate_catalog, verify_price_stock_currency_timestamp y configure_margin_commission_rules.
- GAMMA: separate_confirmed_and_pending_cash, calculate_potential_available_capital, identify_exact_instrument, assess_market_issuer_concentration_liquidity_fx_risks, build_adverse_base_favorable_scenarios y record_price_currency_liquidity_spread_fees.

Los handlers usan exclusivamente datos suministrados, no consultan fuentes externas ni publican cambios. Las propuestas de oportunidad, margen, instrumento y riesgo terminan en HUMAN_REVIEW. GAMMA permanece RESEARCH_ONLY.

Los workers generales también cubren intake/plan/QA básico en ALPHA, oportunidad/consentimiento/comisiones en BETA y research/data-quality/risk-gate en GAMMA. No equivalen a conectores de mercado ni a ejecución comercial externa.

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

CI ejecuta compileall y 63 pruebas unitarias/integración local con Python 3.11. Los tests loopback no sustituyen el handshake remoto, el sandbox del proveedor, la conciliación real ni las pruebas de caída/recuperación del despliegue.
