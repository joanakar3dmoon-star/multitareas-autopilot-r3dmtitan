# Puertas obligatorias antes de producción

1. **Código:** módulos completos, dependencias fijadas, tests unitarios e integración, análisis estático y CI verde.
2. **Persistencia:** base de datos durable, migraciones, idempotencia, backup externo y restauración probada.
3. **IA:** proveedor elegido y probado, límites de gasto, fallback, timeout, privacidad y trazabilidad.
4. **Plataformas:** API oficial, credenciales en gestor de secretos, scopes mínimos, cumplimiento de términos y sandbox/E2E.
5. **Cobros:** webhook firmado, deduplicación, conciliación PSP/banco, devoluciones, chargebacks y cuenta verificada.
6. **SEPA:** distinguir cobros entrantes de transferencias salientes. Activar solo la capacidad necesaria; ninguna transferencia saliente queda autorizada por defecto.
7. **Fiscalidad España:** titular y situación fiscal confirmados, facturación conforme a normativa aplicable, IVA y retenciones separados, revisión profesional cuando corresponda. El ledger no sustituye software de facturación legal.
8. **GAMMA:** RESEARCH_ONLY hasta que exista broker identificado y autorizado, instrumentos permitidos, límites duros, control de exposición, reconciliación y aprobación humana de cada orden real.
9. **Operación 24/7:** health checks, watchdog, reintentos limitados, alertas, rotación de logs, recuperación y prueba de caída.
10. **Go-live:** despliegue separado, backup y rollback; validar endpoints, heartbeats y una operación real controlada. GitHub verde no equivale a producción.

## Parada segura

Ante credenciales inválidas, datos de mercado obsoletos, discrepancia bancaria, riesgo fuera de límite, webhook no verificable, worker sin heartbeat o fallo de QA: bloquear nuevas acciones externas y escalar a revisión humana.
