# Mapa de integraciones a verificar

Inventario inicial de componentes identificados en QUASAR. La presencia de un archivo o workflow no demuestra que la integración esté autenticada, desplegada o autorizada para operar.

| Área | Código/documentación identificada | Reutilización prevista | Validación pendiente |
|---|---|---|---|
| Dealwork | colmena/cliente_dealwork.py, colmena/conectar_dealwork.py y workflow Dealwork | ALPHA y BETA como adaptadores aislados | API vigente, OAuth/permisos, publicación, contrato, cobro y pruebas E2E |
| Workers y Cerebro | módulos quasar/business_workers.py, intelligent_workers.py, bot_families.py, admin_brain.py | Adaptadores de workers y memoria | contratos, límites, persistencia, compatibilidad y pruebas |
| Marketplace | marketplace_outbox.py y documentación de clientes/marketplaces | BETA | plataformas exactas, APIs oficiales, reglas, atribución y liquidación |
| Finanzas | r3dm_finanzas, quasar/payments.py y quasar/work_payments.py | Ledger y conciliación | webhooks reales, titular fiscal, IVA/retenciones, reembolsos y conciliación |
| Verticales | catálogos JSON y vertical_product_factory.py | Catálogo versionado | mapear cada vertical a workers realmente ejecutables |
| Cerebro QUASAR | site_pulpo_brain.py y admin_brain_cycle.py | Integración por API/eventos, nunca acoplamiento directo | endpoint, autenticación, esquema, memoria y pruebas de contrato |
| IA | variables de entorno y módulos existentes | proveedor intercambiable | verificar API, coste, límites, privacidad, disponibilidad y licencia |
| SEPA/banco | configuración y finanzas existentes | conciliación entrante y registro de liquidaciones | proveedor, mandato, OAuth, scopes, webhook y cuenta titular |
| Broker | no se ha verificado un adaptador apto para GAMMA | interfaz futura | broker autorizado, instrumentos, sandbox, límites y autorización explícita |

## Regla
Antes de copiar o importar un módulo existente, revisar su código, pruebas, dependencias, estado de despliegue y permisos. Mantener los sistemas existentes intactos; integrar mediante adaptadores y contratos versionados.
