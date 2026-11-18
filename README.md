# R3DM TITAN — Multitareas Autopilot

**Estado: scaffold inicial aislado; NO está conectado ni desplegado en producción.**

Este repositorio aloja el negocio Multitareas de forma independiente. No sustituye los Pulpos históricos de QUASAR, no modifica Multifunción y no mezcla sus rutas, tablas, credenciales o despliegues.

## Los tres Pulpos

- **ALPHA — Multitareas y servicios autónomos:** automatización de procesos digitales, trabajos por encargo, producción web, páginas y plataformas, operaciones con bots y workers IA.
- **BETA — Marketplace, afiliación y ventas por comisión:** descubrimiento de oportunidades, ofertas, leads, citas, seguimiento, negociación asistida, cierre y conciliación de comisiones. Respeta las reglas y pagos de cada plataforma.
- **GAMMA — Autoinversión no cripto:** investigación y análisis de activos tradicionales, asignación, riesgo, seguimiento y aprendizaje. Sin cripto. El modo inicial es análisis; cualquier orden real requiere broker autorizado, controles de riesgo y aprobación explícita.

## Cerebro común
Un orquestador coordina los tres Pulpos, sus familias de bots, workers, verticales, flujos y ciclos. La integración con Cerebro/Colmena de otros proyectos será mediante adaptadores explícitos y contratos versionados; no se importará código antiguo a ciegas.

## Seguridad económica
- Los agentes pueden preparar trabajos y gestionar cobros/conciliación mediante proveedores autorizados.
- No pueden iniciar gastos, transferencias salientes, compras de créditos, suscripciones ni órdenes de inversión sin autorización humana explícita.
- Cobro recibido no equivale a beneficio neto.
- IVA, retenciones/IRPF, comisiones, devoluciones y costes se registran por separado.
- No se guardan claves, IBAN completos ni credenciales en Git.

## Estado de ejecución
Este primer commit establece contratos y límites de seguridad. No afirma que Dealwork, marketplaces, afiliados, proveedores IA, bancos SEPA o brokers estén conectados. Las integraciones se inventariarán y enlazarán una a una, con pruebas y evidencia antes de activar cada conexión.

## Pruebas
```sh
python -m unittest discover -s tests -v
```
