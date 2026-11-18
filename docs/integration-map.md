# Mapa de integraciones y separación de proyectos

La presencia de código o de una URL configurada no demuestra que una integración esté autenticada, desplegada, autorizada u operativa.

| Sistema | Adaptador en Multitareas | Estado comprobado | Requisito pendiente |
|---|---|---|---|
| Cerebro | Outbox SQLite + puente HMAC r3dm-cerebro-bridge-v1 | El evento se guarda localmente; el envío solo se intenta con endpoint, ruta y secreto explícitos | Endpoint receptor real, contrato confirmado, secreto de 32+ caracteres y handshake/roundtrip remoto |
| Superagente Multifunción | Cliente explícito hacia /api/pulpos/jobs con X-Pulpo-Token | Cliente implementado y desactivado por defecto | PR #4 del Multifunción aún debe integrarse/desplegarse; URL y token de servicio; roundtrip de prueba |
| QUASAR | Sin importación directa ni acceso a su base de datos | Repositorio independiente; reutilización prevista mediante APIs/adaptadores revisados | Definir catálogo/datos que se pueden compartir y validar su API de lectura |
| Ollama | Conector HTTP local | Restringido a localhost, con límites de tamaño y timeout | Instalar modelo local y probar inferencia real en el entorno de ejecución |
| Marketplace/afiliación | Adaptador desactivado | No hay cuentas ni proveedores conectados | API oficial, scopes, términos, sandbox, atribución y conciliación |
| Pagos/PSP | Verificador HMAC genérico + ledger local idempotente | No es integración de Stripe/Bizum/SEPA; pagos quedan pendientes de conciliación | Implementación específica por proveedor, replay protection, endpoint firmado, conciliación PSP/banco |
| Banco | No implementado | Sin conexión bancaria | OAuth read-only, scopes mínimos, consentimientos, matching y pruebas |
| Broker | No implementado | GAMMA es RESEARCH_ONLY | No se habilitará ejecución automática; research tradicional únicamente |

## Contratos de puente

### Cerebro
- Los cambios de estado de las tareas generan eventos mínimos en la outbox local.
- No se exporta el payload de trabajo, emails, datos bancarios ni secretos.
- El dispatcher firma el JSON con HMAC-SHA256 y envía X-R3DM-Signature, X-R3DM-Contract e Idempotency-Key.
- El evento permanece pendiente si no hay configuración, falla el handshake o falla la entrega.
- El endpoint de eventos debe configurarse explícitamente; no se inventa una ruta receptora.

### Superagente Multifunción
- El cliente está separado del puente de eventos a Cerebro: envía trabajos explícitos a la API /api/pulpos/jobs usando X-Pulpo-Token.
- La ruta y autenticación se basan en el contrato de la rama/PR #4 de superagente-autopilot-multifuncion; esa PR no equivale a un servicio desplegado.
- Se requiere MULTIFUNCION_BRIDGE_ENABLED=1, HTTPS, URL y token válidos. No hay reenvío automático de tareas.
- Se rechazan campos sensibles como contraseñas, tokens, IBAN, tarjetas, emails y teléfonos. Enviar solo payload mínimo, autorizado y sin datos personales.

## Regla de arquitectura

Multitareas conserva su propio SQLite, workers, permisos, clientes, configuración y cobros. No se comparte una base de datos con QUASAR ni Multifunción. No se fusionan repositorios ni se modifican sus despliegues. Los puentes son asíncronos, explícitos, idempotentes y fail-closed.
