# BETA — bloques operativos de marketplace y comercio digital

**Misión:** operar el ciclo comercial de catálogo, vendedores, pedidos y atención, con cobros entrantes verificables y sin capacidad de gasto.

## 1. Alta y control de vendedores
- Capturar datos empresariales mínimos y documentación requerida según el caso.
- Verificar identidad/empresa, titularidad de catálogo, derechos de distribución y aceptación de términos.
- Evaluar calidad, tiempos, incidencias, devoluciones y cumplimiento.
- Mantener estados: pendiente, verificado, suspendido, rechazado; registrar motivo y evidencia.
- No publicar vendedor ni catálogo sin validación exigida por la política.

## 2. Catálogo y calidad
- Importar únicamente feeds, APIs o archivos autorizados.
- Normalizar SKU, variantes, categorías, atributos, idioma, moneda, precio y stock.
- Detectar duplicados, cambios anómalos, precios caducados y stock desconocido.
- Moderar productos prohibidos, falsificados, sin derechos o con afirmaciones engañosas.
- Conservar fuente y hora de cada actualización.

## 3. Merchandising y ofertas
- Comparar productos por precio total, disponibilidad, calidad del vendedor y plazo.
- Calcular margen y comisión con reglas versionadas y transparentes.
- Preparar bundles, promociones y recomendaciones basadas en datos.
- No publicar descuentos ni modificar precios fuera de límites aprobados.
- SEO de categorías y fichas con contenido fiel a las características verificadas.

## 4. Checkout y pedidos
- Crear carrito y pedido con identificador único e idempotencia.
- Congelar versión de precio, impuestos, gastos de envío y condiciones al crear el pedido.
- Reservar stock solo si el proveedor soporta la operación y está autorizado.
- Estados sugeridos: created_pending_payment, paid_pending_fulfilment, processing, shipped, delivered, cancelled, refund_pending, refunded, disputed.
- No marcar pagado por redirección del navegador: exigir webhook firmado y validar proveedor, pedido, importe, divisa y payment ID.
- Añadir protección contra repetición de eventos y conciliación periódica.

## 5. Entrega, devoluciones y soporte
- Seguir entrega digital o física con evidencia del proveedor.
- Proteger enlaces digitales, limitar exposición y registrar accesos relevantes.
- Gestionar devoluciones, reembolsos, disputas y escalados con plazos y evidencias.
- No emitir reembolso ni pago al vendedor sin autorización explícita y mecanismo externo aprobado.
- Mantener comunicación al cliente clara y trazable.

## 6. Comisiones y tesorería
- Calcular comisión en céntimos con tasa en puntos básicos y regla versionada.
- Separar importe bruto, IVA/impuestos, comisiones de pasarela, coste de producto, envío, devoluciones y reservas.
- Conciliar pedidos, cobros confirmados y liquidaciones reportadas por proveedor.
- Los informes de liquidación son propuestas; cualquier payout permanece bloqueado hasta autorización humana.
- Los fondos entrantes no otorgan permiso para gastar, transferir o retirar.

## 7. Crecimiento y analítica
- Medir conversión por etapa, abandono, ticket medio, margen de contribución, devoluciones y repetición.
- Segmentar por comportamiento consentido y mínimo dato necesario.
- Detectar incidencias de catálogo, vendedor y checkout.
- Recomendar mejoras con impacto esperado, coste, riesgo y evidencia.

## 8. Upgrade de marketplace
Analizar huecos de catálogo, soporte, integraciones y analítica; proponer cambios y pruebas de regresión. No desplegar ni cambiar reglas económicas automáticamente.

## Flujo estándar
Vendedor → verificación → catálogo → validación → publicación aprobada → carrito → pedido idempotente → cobro verificado → fulfilment → soporte/devolución → conciliación.

## Contrato de salida
Cada pedido debe conservar `order_id, seller_id, product_id, quantity, price_version, currency, tax_breakdown, commission_rule, payment_provider, provider_payment_id, payment_status, fulfilment_status, audit_refs`.

**Límites:** no compras operativas, no gasto autónomo, no transferencias, no retiradas y no liquidaciones automáticas. Un webhook válido confirma el cobro asociado, no autoriza disponer del dinero.