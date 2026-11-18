# Puertas obligatorias antes de producción

1. **Código/API:** handlers previstos, dependencias auditadas, tests unitarios e integración local, análisis estático y CI verde. API protegida con token aleatorio de 32+ caracteres, límites de cuerpo, HTTPS en el edge y revisión de rutas. El catálogo por sí solo no satisface esta puerta.
2. **Persistencia:** SQLite durable, migraciones, idempotencia, outbox, backup externo y restauración probada en un entorno distinto.
3. **IA:** Ollama local instalado y probado; límites de contexto/respuesta, timeout, privacidad y trazabilidad. IA remota permanece desactivada salvo autorización expresa y presupuesto definido.
4. **Plataformas:** API oficial por proveedor, credenciales en gestor de secretos, scopes mínimos, revisión de términos, sandbox y prueba E2E específica.
5. **Cobros entrantes:** webhook específico firmado, protección contra replay, deduplicación, validación de importe/divisa/pedido, conciliación PSP/banco y tratamiento de devoluciones/chargebacks. Un registro local no equivale a dinero liquidado en cuenta.
6. **Dinero saliente:** bloqueado permanentemente para los agentes. Sin gastos, compras, suscripciones, payouts, reembolsos, transferencias ni retiradas autónomas. El titular revisa los cobros liquidados; los agentes no mueven fondos.
7. **Fiscalidad España:** titular y situación fiscal confirmados, facturación conforme a normativa aplicable, IVA, retenciones, comisiones y reservas separados; revisión profesional cuando corresponda. El ledger no sustituye software de facturación legal.
8. **GAMMA:** modo RESEARCH_ONLY permanente. Sin conexión a broker, sin órdenes, sin trading, sin cripto y sin apalancamiento especulativo. Solo investigación de activos tradicionales y propuestas informativas.
9. **Puentes:** endpoint receptor real de Cerebro, secreto rotado, handshake y roundtrip; API de Multifunción integrada/desplegada, token separado, scopes mínimos, idempotencia remota y prueba de payload permitido. Los tests loopback no satisfacen esta puerta.
10. **Operación 24/7:** volumen persistente montado en /data, una sola réplica mientras se use SQLite, health checks, watchdog, alertas, rotación de logs, backup externo, restauración, recuperación tras caída y prueba prolongada de carga.
11. **Go-live:** despliegue separado, rollback, validación de endpoints y una operación real controlada que no permita salidas de dinero. GitHub verde no equivale a producción.

## Parada segura

Ante credenciales inválidas, datos de mercado caducados, discrepancia bancaria, webhook no verificable, worker sin heartbeat, error de firma, fallo de QA o endpoint no autorizado: detener nuevas acciones externas, conservar evidencia y escalar a revisión humana.
