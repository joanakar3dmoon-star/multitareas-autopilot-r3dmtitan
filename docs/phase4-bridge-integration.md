# Fase 4 — contratos de integración entre proyectos

## Objetivo y aislamiento
Multitareas conserva su runtime, SQLite, cola, catálogo, clientes y cobros separados. Los puentes intercambian únicamente estados de tareas hacia Cerebro y encargos acotados hacia Multifunción; no copian bases de datos ni permiten ejecución remota irrestricta.

## Cerebro / QUASAR
- Contrato: `r3dm-cerebro-bridge-v1`.
- Destino: `POST /api/integraciones/multitareas/events`.
- Health: `GET /api/integraciones/multitareas/health`.
- HMAC-SHA256 sobre los bytes exactos del cuerpo.
- `Idempotency-Key` igual a UUID del evento.
- Payload allowlist: `task_id`, `pulpo`, `vertical`, `state`; sin PII, datos de pago, credenciales ni payload de la tarea.
- Outbox durable preexistente; reintento con backoff; marca entregado solo tras ACK de receptor.
- Activación: `MULTITAREAS_CEREBRO_BRIDGE_ENABLED=1`, URL HTTPS y secreto compartido >=32 caracteres.

Receptor previsto en QUASAR PR #123 (en revisión; no desplegado). Verificar merge, CI, deployment y roundtrip antes de activar.

## Superagente Multifunción
- Destino previsto: `POST /api/pulpos/jobs`.
- Bearer token dedicado + `Idempotency-Key`.
- Solo ALPHA/BETA/GAMMA y payload allowlist (`task_id`, `vertical`, `task_key`, `input_ref`).
- No enviar credenciales, clientes, datos bancarios, pagos, ni contenido libre no revisado.
- Activación: `MULTIFUNCION_BRIDGE_ENABLED=1`, URL HTTPS y token >=32 caracteres.

API prevista en Superagente Multifunción PR #4 (en revisión; no desplegada). La forma del endpoint debe confirmarse con su OpenAPI/contrato final antes de la activación. El cliente es deliberadamente explícito y no se ejecuta desde el worker automáticamente.

## No activado
Ambos adaptadores están deshabilitados por defecto. CI local/mocks no verifican DNS, TLS, secretos, autenticación, endpoints en hosting ni persistencia de los servicios remotos.

## Límites financieros permanentes
No existen rutas de gasto, transferencia, payout, reembolso, retiro, suscripción o broker. Los cobros se registran como evidencia entrante, pendientes de conciliación específica. GAMMA es solo investigación de activos tradicionales.
