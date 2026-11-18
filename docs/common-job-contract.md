# Contrato común de ejecución — ALPHA, BETA y GAMMA

Este contrato unifica el formato de trabajo sin mezclar las responsabilidades de cada pulpo.

## Envolvente de trabajo
Todo job debe incluir:
- `job_id`: identificador único e idempotente.
- `pulpo`: ALPHA, BETA o GAMMA.
- `block` y `task`: módulo y tarea declarados en el catálogo.
- `payload_version`: versión del esquema.
- `source_refs`, `observed_at`, `expires_at` y `evidence`.
- `assumptions`, `missing_data`, `cost_estimate`, `risk_level`.
- `compliance_checks`, `approval_required`, `approval_status`.
- `status`, `result`, `error`, `created_at`, `updated_at`.

## Estados
`draft → queued → running → completed` o `awaiting_connector / awaiting_review / blocked / failed`.
No convertir automáticamente un estado pendiente en completado. Los reintentos deben respetar idempotencia y no duplicar pedidos, eventos ni efectos externos.

## Evidencia y datos
- Toda cifra externa debe tener fuente, unidad, moneda y timestamp.
- Distinguir dato observado, dato calculado, hipótesis y dato ausente.
- No inventar proveedores, clientes, ventas, conversiones, precios, pagos ni rentabilidades.
- Los datos caducados deben marcarse y no usarse como actuales.
- Registrar versión del cálculo y supuestos reproducibles.

## Permisos por defecto
- Lectura e investigación: solo fuentes autorizadas y con límites de uso.
- Escritura interna: solo en el ámbito asignado y con auditoría.
- Publicación, contacto externo, cambio de precio, devolución, liquidación o modificación de configuración: aprobación explícita según política.
- Gastos, compras, transferencias y retiradas: denegados a los tres pulpos.
- GAMMA no puede comprar, vender ni cursar órdenes de inversión.
- ALPHA puede preparar campañas y propuestas, no contratar ni comprar activos.
- BETA puede verificar cobros entrantes, no disponer de los fondos ni pagar a vendedores.

## Separación económica
Mantener libros separados para bruto cobrado, IVA/impuestos, comisiones, costes, devoluciones, reservas y neto. El IVA/impuestos recaudados no son beneficio. Solo cobros confirmados y conciliados cuentan como caja confirmada; reservas y obligaciones se descuentan antes de calcular capital potencialmente disponible.

## Upgrade y autonomía
Los workers pueden detectar carencias y proponer mejoras. Ningún worker puede reescribir código, cambiar permisos, instalar dependencias, publicar versiones o desplegar por sí mismo. Todo upgrade exige revisión, pruebas, análisis de seguridad, regresión y aprobación humana.

## Criterios comunes de aceptación
1. Esquema validado y versionado.
2. Fuente/evidencia trazable o estado awaiting_connector.
3. Idempotencia y control de duplicados.
4. Permisos mínimos y rechazo de acciones prohibidas.
5. Registro de auditoría sin secretos.
6. Errores y datos ausentes explícitos.
7. Ningún efecto externo sin conector real, credenciales en hosting y autorización.
8. Ninguna afirmación de producción hasta verificar integración y operación real.
