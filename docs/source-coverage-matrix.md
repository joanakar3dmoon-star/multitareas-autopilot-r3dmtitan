# Matriz de cobertura del runtime — tres Pulpos

**Propósito:** distinguir catálogo funcional, operación local implementada y dependencia externa. Esta matriz refleja la inspección del código de la rama; no es una certificación de producción.

## ALPHA

| Operación | Estado en ejecutor | Alcance real |
|---|---|---|
| `alpha.rank_opportunities` | Implementada localmente | Valida y ordena oportunidades con evidencia y neto estimado |
| `alpha.propose_upgrade` | Implementada localmente | Genera propuesta; no modifica workers ni despliega |
| `collector.fetch_json` | Transporte genérico implementado | Requiere URL por variable de entorno, host allowlist y fuente autorizada |
| Investigación de nichos, afiliación, SEO, CRM y activos digitales | Catálogo/registro; conector o handler específico pendiente | No se debe reportar como ejecución real hasta cablear y validar cada tarea |
| Cuatro familias de recolectores de oro | Registradas; adaptadores especializados pendientes | El fetch genérico no interpreta por sí mismo pureza, primas, comisiones, liquidez o cadena de suministro |

## BETA

| Operación | Estado en ejecutor | Alcance real |
|---|---|---|
| `beta.create_order` | Implementada localmente | Crea pedido pendiente de pago; exige stock conocido y listing validado |
| `beta.confirm_payment_webhook` | Implementada localmente | Verifica HMAC, tipo de evento, pedido, importe, divisa y payment ID |
| Catálogo, onboarding, fulfilment, devoluciones, disputas y conciliación | Catálogo/registro; handlers y conectores específicos pendientes | No implica conexión a proveedor, envío, reembolso ni liquidación |
| Liquidación de vendedores | Bloqueada por política | El estado de pago no concede permiso de payout ni de transferencia |

## GAMMA

| Operación | Estado en ejecutor | Alcance real |
|---|---|---|
| `gamma.propose_allocation` | Implementada localmente | Crea propuesta usando efectivo confirmado menos reservas |
| `gamma.execute` | Rechazada explícitamente | No compra, vende, transfiere ni cursa órdenes |
| Recolectores, fundamentales, valoración, macro, escenarios y cartera | Catálogo/registro; conectores y analizadores específicos pendientes | No afirmar análisis de mercado actualizado sin datos y fuentes verificables |
| Seguimiento y alertas | Catálogo/registro; integración de proveedor pendiente | No existe garantía de monitorización hasta configurar y verificar fuentes |

## Capa común

- `RotatingScheduler`: cola SQLite, turnos por familia, límite de concurrencia, leases y recuperación de trabajos caducados.
- `dispatch_once`: reclama un trabajo, llama al ejecutor y registra resultado; los fallos se marcan sin reintento automático en el runtime inspeccionado.
- `providers.fetch_json_source`: exige HTTPS, allowlist de hosts y variables de entorno; no incluye selección automática de proveedor ni transforma respuestas a modelos de dominio.
- `api.py`: expone health, status y enqueue con token de servicio; no demuestra por sí solo que el proceso worker esté desplegado.
- `worker.py`: proceso continuo que registra pulpos y consulta la outbox. El envío al Cerebro depende de que el bridge tenga configuración y conexión verificadas.
- `integration.py` y `bridge_dispatcher.py`: puente y outbox presentes en el repositorio; conexión remota no certificada por esta inspección.

## Próximas unidades de implementación (sin ejecutar todavía pruebas integrales)

1. Definir un dispatcher por `pulpo + block + task`, con allowlist estricta derivada del registro.
2. Añadir validadores de payload versionados por tarea y rechazar combinaciones worker/pulpo/bloque no válidas.
3. Añadir handlers de dominio para las familias de ALPHA, operaciones de BETA y análisis de GAMMA; mantener awaiting_connector cuando falten fuentes.
4. Completar idempotencia de eventos, reintentos con política explícita y trazabilidad de cada job.
5. Añadir pruebas unitarias y de integración al terminar los bloques, antes de conectar Cerebro o desplegar.

## Condición de veracidad

Una tarea solo puede marcarse `completed` si el handler terminó con salida válida y evidencia suficiente. La existencia en `registry.py`, `catalogo_funcional.json` o `especificaciones_tareas.json` significa que está definida/registrada, no que tenga un conector, datos actuales o despliegue activo.
