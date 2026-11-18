# Mapa de integraciones a verificar en QUASAR

Inventario inicial basado en el árbol de GitHub inspeccionado. La presencia de un archivo o workflow no demuestra que la integración esté autenticada, desplegada o autorizada para operar.

| Área | Código/documentación existente | Reutilización prevista | Validación pendiente |
|---|---|---|---|
| Dealwork | `colmena/cliente_dealwork.py`, `colmena/conectar_dealwork.py`, `scripts/dealwork_radar.py`, workflow Dealwork | ALPHA y BETA como adaptadores aislados | API vigente, OAuth/permisos, publicación, contrato, cobro y pruebas E2E |
| Workers y Cerebro | `quasar/business_workers.py`, `quasar/intelligent_workers.py`, `quasar/bot_families.py`, `quasar/admin_brain.py` | Adaptadores de workers y memoria | contratos, límites, persistencia, compatibilidad y pruebas |
| Marketplace | `quasar/marketplace_outbox.py`, documentos de clientes/marketplaces | BETA | plataformas exactas, APIs oficiales, reglas, atribución y liquidación |
| Finanzas | `r3dm_finanzas/engine.py`, `r3dm_finanzas/worker_ai.py`, `quasar/payments.py`, `quasar/work_payments.py` | Ledger y conciliación | webhooks reales, titular fiscal, IVA/retenciones, reembolsos y conciliación |
| Verticales y fábrica | `docs/catalogo_verticales_comerciales.json`, `docs/matriz_verticales_ejecutables.json`, `quasar/vertical_product_factory.py` | Catálogo versionado y validado | mapear cada vertical a workers realmente ejecutables |
| Cerebro QUASAR | `quasar/site_pulpo_brain.py`, `quasar/admin_brain_cycle.py` | Integración por API/eventos, nunca acoplamiento directo | endpoint, autenticación, esquema, memoria y pruebas de contrato |
| IA | variables de entorno en `.env.example` y módulos existentes | proveedor intercambiable | verificar API, coste, límites, privacidad, disponibilidad y licencia |
| SEPA/banco | configuración y finanzas existentes | conciliación entrante y registro de liquidaciones | proveedor bancario/PSP, mandato, OAuth, scopes, webhook y cuenta titular |
| Broker | no se ha verificado un adaptador de broker apto para GAMMA | interfaz futura | broker autorizado, instrumentos, sandbox, límites y autorización explícita |

## Regla

Antes de copiar o importar un módulo existente, revisar su código, pruebas, dependencias, estado de despliegue y permisos. Mantener los sistemas existentes intactos; integrar mediante adaptadores y contratos versionados.
