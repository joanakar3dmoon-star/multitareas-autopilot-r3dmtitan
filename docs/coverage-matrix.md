# Matriz de cobertura real — Multitareas Autopilot

Última revisión: 18/11/2026. Esta matriz describe código presente y pruebas CI; no certifica producción.

## ALPHA — 37 tareas declaradas; 17 handlers específicos

| Capacidad | Estado | Evidencia/limitación |
|---|---|---|
| Intake, brief, planificación y QA básico | Implementada localmente | AlphaBotWorker; no ejecuta trabajos externos |
| Registro estructural de fuentes | Implementado localmente | HTTPS/proveedor/timestamp; no hace fetch ni verifica licencia |
| Puntuación de oportunidades y problemas de clientes | Implementada localmente | Agrega registros y puntuaciones aportadas; requiere revisión humana |
| Comparación de comisiones afiliadas | Implementada localmente | Compara términos aportados; no consulta programas ni verifica elegibilidad |
| Upgrade — oro físico spot | 4 handlers | Valida quotes, normaliza divisa/unidad/pureza, calcula spreads/costes y registra disponibilidad |
| Upgrade — instrumentos vinculados | 3 handlers | Identifica issuer, revisa fees/liquidez y registra riesgos con límites aportados |
| Upgrade — supply chain | 3 handlers | Estructura proveedores, revisa fechas de certificados y compara MOQ/logística |
| Upgrade — diferenciales de mercado | 3 handlers | Normaliza peso/pureza/divisa/impuestos/envío, compara ofertas y registra evidencias |
| Conectores reales de feeds de oro/metales y proveedores | Pendiente | Los handlers Upgrade procesan datos suministrados; no consultan fuentes remotas |
| SEO, CRM, embudos y activos digitales | Pendiente | Sin conectores ni publicación externa |

## BETA — 29 tareas declaradas; 6 handlers específicos

| Capacidad | Estado | Evidencia/limitación |
|---|---|---|
| Clasificación de oportunidades, cualificación con consentimiento y conciliación aritmética de comisiones | Implementada localmente | No verifica ofertas ni concilia con PSP |
| Cálculo de precio total y margen/comisión | Implementado localmente | No crea checkout ni publica reglas |
| Cálculo neto tras reservas | Implementado localmente | Excluye cobros pendientes y separa IVA, impuestos, fees, devoluciones, costes y reserva |
| Normalización de SKU, variantes y categorías | Implementada localmente | Solo prepara salida; no modifica catálogo externo |
| Detección de duplicados | Implementada localmente | Informa duplicados; no elimina registros |
| Validación estructural de precio, stock, divisa y timestamp | Implementada localmente | No verifica stock/precio remoto ni frescura |
| Alta de vendedores, catálogo, checkout, pedidos, fulfillment, pagos y devoluciones | Pendiente | Marketplace adapter desactivado |
| Liquidaciones de vendedores | Bloqueadas por política | No hay payouts ni transferencias autónomas |

## GAMMA — 15 tareas declaradas; 6 handlers específicos

| Capacidad | Estado | Evidencia/limitación |
|---|---|---|
| Allowlist de activos tradicionales y exclusión cripto | Implementada localmente | ResearchBot admite equity, ETF, bond, fund, gold y commodity; nunca emite órdenes |
| Validación estructural de precio/timestamp y gate de exposición | Implementada localmente | No verifica frescura; riesgo sin datos explícitos queda NOT_EVALUATED |
| Identificación estructural de instrumento | Implementada localmente | No verifica identidad con fuente primaria |
| Evaluación de concentración, liquidez y FX | Implementada localmente | Compara entradas con límites suministrados; requiere revisión humana |
| Escenarios adverso/base/favorable | Implementados localmente | Aritmética sobre supuestos aportados; no es previsión |
| Registro de precio, bid/ask, spread, volumen y fees | Implementado localmente | No verifica fuente ni actualidad |
| Separación de efectivo confirmado y pendiente | Implementada localmente | El pendiente nunca se considera disponible |
| Cálculo de capital potencial tras reservas | Implementado localmente | Solo usa efectivo confirmado y termina en HUMAN_REVIEW |
| Feeds, fundamentales, valoración, escenarios de mercado y alertas | Pendiente | Sin proveedores de datos conectados |
| Broker, trading y cripto | Prohibidos | GAMMA permanece RESEARCH_ONLY; no se conectará ejecución de órdenes |

## Núcleo y puentes

- SQLite: cola persistente, idempotencia, auditoría, leases, recuperación y outbox de eventos mínimos.
- Catálogo: 81 tareas cargadas y validadas; 29 handlers deterministas locales (ALPHA 17, BETA 6, GAMMA 6). Las tareas restantes sin handler quedan en NEEDS_ADAPTER.
- CI: 84 pruebas unitarias y de integración local superadas en GitHub Actions con Python 3.11 y compileall.
- Cerebro: evento local y cliente HMAC preparado; roundtrip loopback validado, falta endpoint receptor real, ruta confirmada y roundtrip remoto.
- Multifunción: cliente explícito a /api/pulpos/jobs; handoff loopback validado, permanece desactivado por defecto y la API objetivo del otro repositorio no se considera desplegada.
- Pagos: helper HMAC genérico y ledger local idempotente; no es integración de Stripe/Bizum ni conciliación bancaria.
- IA: adaptador Ollama local y planificador por catálogo; no se ha probado una inferencia real en el hosting.
- Hosting: no desplegado; no hay disponibilidad 24/7 demostrada.

## Regla de estado

Los handlers Upgrade no realizan fetch remoto: necesitan fuentes autorizadas y datos suministrados. Una tarea de catálogo sin handler se mantiene en NEEDS_ADAPTER. Una tarea con datos incompletos no se marca como verificada. Un evento en outbox no se considera entregado hasta recibir acuse positivo. Un cobro no se considera conciliado por existir en el ledger.
