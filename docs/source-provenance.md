# Procedencia y límites del primer traslado

El scaffold funcional se trasladó desde el subdirectorio `multitareas-autopilot-r3dmtitan/` de `joanakar3dmoon-star/quasar-autopilot`, rama `backup/multitareas-autopilot-pr121-20261118`, commit fuente `6ecf5766628c3b2cb27246ffb213ec48ac16d7ed` (PR #121).

Se trasladaron únicamente los 14 archivos del módulo dedicado: README, ejemplo de entorno, contratos del Cerebro/orquestador/permisos, tres Pulpos, documentación y test inicial. No se copió el árbol raíz de QUASAR ni sus otros negocios, workers, finanzas, frontend, secretos o despliegues.

El código es un scaffold inicial: los workers ALPHA/BETA devuelven revisión humana y GAMMA permanece RESEARCH_ONLY. No se debe presentar como integración operativa, autónoma ni producción. Las conexiones externas requieren auditoría y pruebas de contrato específicas.
