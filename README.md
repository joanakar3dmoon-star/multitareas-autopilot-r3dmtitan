# R3DM TITAN — Multitareas Autopilot

**Estado: base inicial importada; todavía no está conectada ni desplegada en producción.**

Este repositorio es el negocio independiente **Multitareas Autopilot** dentro del ecosistema R3DM/TITAN. Mantiene código, configuración, datos, clientes, operaciones y cobros separados de QUASAR y de Superagente Multifunción. Puede reutilizar servicios compartidos mediante adaptadores explícitos y contratos versionados, sin acoplar ni sustituir los proyectos existentes.

## Objetivo operativo

Autonomía de extremo a extremo en tareas comerciales y operativas permitidas, con supervisión automática, recuperación, trazabilidad y alertas. La única comprobación rutinaria del titular será verificar que los cobros liquidados han llegado a su cuenta. Esto requiere integrar y probar PSP/banco, webhooks firmados y conciliación; no se considera implementado por esta base inicial.

## Los tres Pulpos

- **ALPHA — Multitareas y servicios autónomos:** captación y análisis de encargos, planificación, automatización, desarrollo web, diseño, contenido, datos, QA, entrega y soporte.
- **BETA — Marketplace, afiliación y ventas:** oportunidades, catálogo, ofertas, leads, pedidos, seguimiento, atribución y conciliación de comisiones.
- **GAMMA — Investigación de inversión tradicional:** acciones, ETF, fondos, bonos, oro y materias primas. Sin criptomonedas. Modo inicial `RESEARCH_ONLY`; no envía órdenes de inversión.

## Límites financieros invariables

- Se permiten cobros entrantes únicamente mediante proveedores autorizados, webhooks verificados y conciliación.
- Los agentes no pueden gastar, comprar, contratar suscripciones, transferir, retirar ni mover fondos.
- No se conceden permisos financieros a un agente por decisión del propio agente.
- IVA, retenciones, comisiones, devoluciones, costes y beneficio neto se contabilizan por separado.
- No se inventan ventas, clientes, saldos ni cobros. No se guardan secretos, credenciales ni IBAN completos en Git.

## Estructura

- `core/`: cerebro, orquestación y permisos.
- `pulpos/`: ALPHA, BETA y GAMMA.
- `docs/`: arquitectura, inventario de integraciones y puertas de producción.
- `tests/`: pruebas iniciales.

## Hitos de implementación

1. Completar los bloques operativos de ALPHA, BETA y GAMMA.
2. Especializar el agente central para planificar, priorizar, coordinar y recuperar tareas.
3. Implementar bots, submódulos, persistencia y conectores ejecutables.
4. Construir puentes seguros con Cerebro y Multifunción, conservando la separación entre proyectos.
5. Ejecutar pruebas integrales, validar cobros reales de forma controlada y preparar producción.

## Pruebas iniciales

```sh
python -m unittest discover -s tests -v
```

La presencia de código no demuestra que una API, proveedor, banco o marketplace esté conectado. No activar producción hasta superar las puertas descritas en `docs/production-gates.md`.
