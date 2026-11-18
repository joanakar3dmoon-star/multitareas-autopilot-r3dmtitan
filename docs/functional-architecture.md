# Especificación funcional completa — ALPHA, BETA y GAMMA

Estado: especificación funcional para completar la implementación. Esta documentación no declara conectores, workers, proveedores ni producción activos.

## Principios comunes
- Tres unidades empresariales independientes: ALPHA, BETA y GAMMA.
- Cada bloque incluye: objetivo, entradas, validaciones, salida estructurada, estado, trazabilidad, errores y métricas.
- Los trabajos se ejecutan mediante la cola persistente y el worker existente; no se debe crear un segundo scheduler paralelo.
- Toda oportunidad debe incluir fuente, fecha de consulta, evidencia, coste, riesgo, restricciones y siguiente acción.
- Estados normalizados: draft, queued, running, awaiting_connector, awaiting_review, blocked, completed, failed.
- No inventar datos, leads, stock, precios, comisiones, pagos, rentabilidades ni ingresos.
- No ejecutar compras, ventas de activos, transferencias, retiradas ni gastos autónomos.
- Las publicaciones, campañas, mensajes comerciales y compromisos externos requieren autorización y controles de cumplimiento.
- Los secretos se configuran en el hosting; nunca se almacenan en Git.

# ALPHA — Afiliación, investigación comercial y recolectores Upgrade

## A. Inteligencia de mercado
1. Descubrimiento de nichos y subnichos.
2. Análisis de demanda, intención y estacionalidad.
3. Investigación de competidores y posicionamiento.
4. Detección de problemas de clientes y necesidades no cubiertas.
5. Matriz de oportunidad: demanda, competencia, margen estimado, coste de entrada, riesgo y evidencia.
6. Registro de fuentes y fecha de verificación.

## B. Afiliación
1. Catálogo de programas y redes de afiliación.
2. Requisitos, países admitidos, términos y restricciones.
3. Comisiones, recurrencia, atribución, cookies y ventanas de conversión.
4. Comparación de programas y selección por evidencia.
5. Registro de enlaces y campañas por canal.
6. Seguimiento de clics, leads, conversiones y comisiones confirmadas.
7. Conciliación de comisiones pendientes, aprobadas, rechazadas y pagadas.
8. Alertas por cambios de términos, comisiones o disponibilidad.
9. Bloqueo de promoción engañosa o sin disclosure publicitario.

## C. Recolectores Upgrade — cuatro familias
1. Oro físico/spot: fuentes de cotización autorizadas, fecha, moneda, unidad, spread, costes y disponibilidad.
2. Instrumentos vinculados al oro: identificación del instrumento, emisor, estructura, comisiones, liquidez y riesgos; solo análisis informativo.
3. Cadena de suministro: proveedores, origen declarado, certificaciones verificables, mínimos, logística, plazos y costes.
4. Diferencias de mercado/ofertas: comparación normalizada por unidad, pureza cuando aplique, divisa, impuestos, transporte, spread y fecha.

Los recolectores no compran, venden, reservan ni ejecutan órdenes. No llaman “beneficio” a una diferencia teórica. Cada hallazgo se guarda como oportunidad pendiente de revisión.

## D. Activos digitales y captación
1. Investigación de productos digitales vendibles.
2. Validación de derechos, licencias y permisos.
3. Brief de producto, público objetivo y propuesta de valor.
4. Generación asistida de landing, fichas, lead magnets y contenidos.
5. SEO: palabras clave, intención, arquitectura y auditoría.
6. Embudos: captación, consentimiento, cualificación y seguimiento.
7. Automatizaciones de CRM: deduplicación, etiquetado, scoring y tareas.
8. Analítica: tráfico, conversión, CAC y ROI solo con datos medidos.

## E. Entregables y métricas
Oportunidad documentada, programa afiliado evaluado, campaña en borrador, activo digital propuesto, lead con consentimiento y reporte de rendimiento. Métricas: oportunidades verificadas, fuentes válidas, comisiones confirmadas, conversión y coste por adquisición.

# BETA — Marketplace y comercio digital

## A. Vendedores y catálogo
1. Alta de vendedor y checklist KYC/KYB según proveedor y jurisdicción.
2. Verificación de identidad comercial y documentación aplicable.
3. Aceptación de términos y política de vendedores.
4. Importación de catálogo desde conectores autorizados.
5. Normalización de atributos, SKU, variantes y categorías.
6. Deduplicación y detección de productos inconsistentes.
7. Verificación de precio, stock, moneda, disponibilidad y timestamp.
8. Gestión de imágenes, descripciones, licencias y derechos.
9. Moderación de contenido, productos prohibidos y reclamaciones.

## B. Oferta y merchandising
1. Comparador de productos y vendedores.
2. Cálculo transparente de precio total: producto, envío, impuestos y tasas.
3. Reglas de margen y comisión configurables.
4. Promociones con fechas, condiciones y límites.
5. SEO de catálogo y calidad de fichas.
6. Recomendaciones basadas en datos, sin reseñas ni escasez inventadas.

## C. Pedidos y operaciones
1. Carrito y checkout.
2. Creación de pedido con identificador idempotente.
3. Reserva lógica de stock solo si el proveedor lo soporta.
4. Confirmación de pago mediante webhook firmado o conciliación.
5. Validación de pedido, importe, divisa, proveedor e identificador.
6. Gestión de estados: created, pending_payment, paid, processing, shipped, delivered, cancelled, refunded, disputed.
7. Entrega digital protegida o seguimiento logístico.
8. Devoluciones, cancelaciones, reembolsos y disputas.
9. Atención al cliente y escalado humano.
10. Conciliación de pedidos, comisiones y liquidaciones.

## D. Tesorería y límites
- Un checkout o pedido no es ingreso confirmado.
- IVA, impuestos, devoluciones, comisiones del proveedor y reservas se separan antes de calcular neto.
- La liquidación al vendedor exige pago confirmado, conciliación y autorización del titular.
- BETA no puede retirar fondos, transferir dinero ni pagar gastos por iniciativa propia.

## E. Entregables y métricas
Vendedor revisado, catálogo validado, oferta, pedido trazable, pago confirmado, entrega acreditada, incidencia y conciliación. Métricas: conversión, ticket medio, margen neto estimado/real, devoluciones, disputas y tiempo de entrega.

# GAMMA — Inteligencia de inversión tradicional (sin cripto ni trading automático)

## A. Universo permitido
Oro y metales, acciones cotizadas, ETF, fondos, bonos, deuda pública y materias primas mediante instrumentos regulados. Excluir criptomonedas, derivados apalancados y productos que la política de riesgo prohíba.

## B. Investigación y análisis
1. Identificación del activo e instrumento exacto.
2. Fuentes primarias y fecha de los datos.
3. Precio, divisa, liquidez, spread, comisiones y fiscalidad aplicable.
4. Análisis fundamental cuando proceda.
5. Riesgos de mercado, emisor, concentración, liquidez y divisa.
6. Escenarios adverso/base/favorable sin prometer rentabilidad.
7. Comparación con alternativas y coste de oportunidad.
8. Horizonte, tesis, catalizadores y condiciones que invalidan la tesis.
9. Informe con incertidumbres y datos faltantes.
10. Revisión periódica y alertas informativas.

## C. Capital y reservas
1. Diferenciar saldo bancario, cobros pendientes, ingresos confirmados y capital disponible.
2. Separar IVA, impuestos, devoluciones, gastos comprometidos y reserva operativa.
3. Mantener reserva de emergencia definida por el titular.
4. Calcular capital potencialmente disponible solo con datos conciliados.
5. Presentar propuestas para aprobación humana.

## D. Límites operativos
GAMMA es un módulo de investigación y apoyo a decisiones. No da órdenes a brokers, no abre cuentas, no compra ni vende activos, no mueve fondos y no promete rendimientos. Cualquier inversión real queda fuera del worker y requiere decisión y ejecución humana por canales autorizados.

## E. Entregables y métricas
Ficha de activo, comparativa, informe de riesgo, tesis, alerta y propuesta pendiente de aprobación. Métricas: cobertura de fuentes, frescura de datos, riesgos identificados y desviación entre hipótesis y datos observados.

# Ciclo común de trabajo
1. Descubrir necesidad u oportunidad.
2. Recopilar datos de fuentes autorizadas.
3. Validar calidad, vigencia y procedencia.
4. Calcular costes, riesgos y reservas.
5. Preparar propuesta.
6. Aplicar puerta de revisión humana cuando exista impacto externo, financiero, legal o reputacional.
7. Encolar únicamente tareas autorizadas.
8. Ejecutar mediante worker registrado.
9. Guardar resultado, evidencia y errores.
10. Publicar evento interno para futura integración con Cerebro.
11. Medir resultados confirmados.
12. Aprender de resultados sin auto-modificar código ni políticas.

## Contrato mínimo de cada trabajo
- job_id, pulpo, bloque, tarea, payload_version
- source_refs[], observed_at, expires_at
- evidence[], assumptions[], missing_data[]
- cost_estimate, risk_level, compliance_checks[]
- approval_required, approval_status
- status, result, error, created_at, updated_at

## Criterios de aceptación funcional
- Los tres pulpos tienen catálogo de bloques y tareas consultable.
- Cada tarea declara entradas, validaciones, salida y permisos.
- Sin fuente configurada, el resultado es awaiting_connector.
- Sin aprobación requerida, la tarea permanece awaiting_review.
- Los eventos y resultados son trazables e idempotentes.
- Los límites financieros se aplican en servidor, no solo en la interfaz.
- No se declara producción ni autonomía 24/7 por la mera presencia del código.
