# Matriz de cobertura real — Multitareas Autopilot

Última revisión: 18/11/2026. Esta matriz describe código presente y pruebas CI; no certifica producción.

## ALPHA — 37 tareas declaradas

| Capacidad | Estado | Evidencia/limitación |
|---|---|---|
| Validación de intake y preparación de brief | Implementada localmente | AlphaBotWorker + IntakeBot |
| Planificación de trabajo por vertical | Implementada localmente | PlannerBot produce pasos; no ejecuta el trabajo externo |
| QA básico de artefacto | Implementado localmente | Comprueba contenido/referencia y scope; no es QA profundo |
| Registro estructural de fuentes | Implementado localmente | Exige URL HTTPS, proveedor y timestamp; no hace fetch ni verifica licencia |
| Puntuación de oportunidades | Implementada localmente | Fórmula versionada sobre cuatro puntuaciones aportadas; requiere revisión humana |
| Inteligencia de nichos, demanda y competidores | Pendiente | Sin fuentes ni handlers específicos |
| Programas de afiliación, atribución y conversiones | Pendiente | Sin redes conectadas ni conciliación externa |
| Cuatro familias de recolectores Upgrade | Declaradas | Sin feeds de oro/metal ni adaptadores de proveedor |
| SEO, CRM, embudos y activos digitales | Pendiente | Sin conectores ni publicación externa |

## BETA — 29 tareas declaradas

| Capacidad | Estado | Evidencia/limitación |
|---|---|---|
| Clasificación de oportunidades aportadas | Implementada localmente | Ordena candidatos por comisión declarada; no verifica la oferta |
| Cualificación de lead con permiso explícito | Implementada localmente | Puntúa campos aportados y conserva el flag de consentimiento; no contacta |
| Conciliación aritmética de comisiones | Implementada localmente | Unidades monetarias menores y moneda de tres letras; no concilia con PSP |
| Cálculo de precio total | Implementado localmente | Suma producto, envío, impuestos y fees suministrados; no crea checkout |
| Cálculo neto tras reservas | Implementado localmente | Excluye cobros pendientes y separa IVA, impuestos, fees, devoluciones, costes y reserva |
| Alta de vendedores y catálogo | Pendiente | Marketplace adapter desactivado |
| Checkout, pedidos, pagos, fulfillment y devoluciones | Pendiente | No hay API de marketplace ni PSP conectada |
| Liquidaciones de vendedores | Bloqueadas por política | El estado de pago no concede permiso de payout ni transferencia |

## GAMMA — 15 tareas declaradas

| Capacidad | Estado | Evidencia/limitación |
|---|---|---|
| Allowlist de clases tradicionales y exclusión cripto | Implementada localmente | ResearchBot rechaza cripto y no emite órdenes |
| Validación estructural de precio/timestamp | Implementada localmente | No verifica frescura ni fuente |
| Gate de exposición | Implementado con entradas explícitas | Sin datos de riesgo devuelve NOT_EVALUATED; nunca autoriza órdenes |
| Separación de efectivo confirmado y pendiente | Implementada localmente | El pendiente nunca se considera disponible |
| Cálculo de capital potencial tras reservas | Implementado localmente | Solo usa efectivo confirmado y termina en HUMAN_REVIEW |
| Fuentes primarias, fundamentales, valoración y escenarios | Pendiente | No hay feeds ni analistas de dominio conectados |
| Cartera y alertas | Pendiente | No hay datos bancarios ni servicio de monitorización |

## Núcleo y puentes

- SQLite: cola persistente, idempotencia, auditoría, leases, recuperación y outbox de eventos mínimos.
- Catálogo: 81 tareas cargadas y validadas; 6 handlers deterministas locales registrados. Las tareas restantes sin handler quedan en NEEDS_ADAPTER.
- CI: suite unitaria Python 3.11 y compileall; consultar el último workflow para el recuento verificado.
- Cerebro: evento local y cliente HMAC preparado; falta endpoint receptor real, ruta confirmada y roundtrip remoto.
- Multifunción: cliente explícito a /api/pulpos/jobs, desactivado por defecto; la API objetivo está en PR #4 del otro repositorio y no se considera desplegada.
- Pagos: helper HMAC genérico y ledger local idempotente; no es integración de Stripe/Bizum ni conciliación bancaria.
- IA: adaptador Ollama local; no se ha probado una inferencia real en el hosting.
- Hosting: no desplegado; no hay disponibilidad 24/7 demostrada.

## Regla de estado

Una tarea de catálogo sin handler se mantiene en NEEDS_ADAPTER. Una tarea con datos incompletos no se marca como verificada. Un evento en outbox no se considera entregado hasta recibir respuesta HTTP satisfactoria. Un cobro no se considera conciliado por existir en el ledger.
