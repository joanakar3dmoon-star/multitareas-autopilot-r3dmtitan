# Estado de hitos — 18/11/2026

Este documento separa el código integrado de las dependencias externas aún no verificadas.

## Hito 1 — Bloques ALPHA/BETA/GAMMA

PARCIAL

- Catálogo: 81 tareas declaradas (ALPHA 37, BETA 29, GAMMA 15).
- Handlers locales: 29 (ALPHA 17, BETA 6, GAMMA 6).
- Las 13 tareas Upgrade de las cuatro familias ALPHA ya validan y calculan sobre datos suministrados.
- Quedan 52 tareas sin handler específico. El runtime las deja en NEEDS_ADAPTER; no simula ejecución.

## Hito 2 — Cerebro y planificador

PARCIAL

- Planificador central asistido por IA: solo propone tareas del catálogo y no las ejecuta.
- Proveedor local Ollama preparado; inferencia real en hosting aún no probada.
- No se permite que el planificador cambie permisos ni ejecute acciones financieras.

## Hito 3 — Bots, submódulos y runtime

IMPLEMENTADO EN LOCAL

- Runtime, cola SQLite, leases, recuperación, idempotencia, auditoría y outbox.
- 29 handlers deterministas.
- API HTTP autenticada para enviar tareas, consultar estado, ver cobertura y pedir planes.
- Worker thread integrado, Dockerfile y health check.
- 84 pruebas de CI superadas en el repositorio Multitareas; la imagen Docker se construye sin publicar.

## Hito 4 — Puentes con Cerebro y Multifunción

EN REVISIÓN

- Multitareas → Cerebro: cliente HMAC implementado. Receptor propuesto en QUASAR PR #123:
  https://github.com/joanakar3dmoon-star/quasar-autopilot/pull/123
- Multitareas → Multifunción: cliente explícito a /api/pulpos/jobs, con token separado y clave de idempotencia.
- La API receptora y la persistencia de idempotencia están en PR #4 de Multifunción:
  https://github.com/joanakar3dmoon-star/superagente-autopilot-multifuncion/pull/4
- Ambos PR siguen abiertos. No se ha hecho merge, despliegue ni roundtrip remoto.

## Hito 5 — Pruebas integrales y producción

PARCIAL

- Superadas: 84 pruebas unitarias/integración local, compileall y build Docker en Multitareas.
- Pendiente: integración remota QUASAR/Multifunción, marketplace, PSP, conciliación bancaria, modelo IA real, backup externo, recuperación, carga y disponibilidad 24/7.
- Las acciones de GitHub de QUASAR y Multifunción aparecen como fallidas sin pasos/logs disponibles en la respuesta de la integración. No se puede atribuir el fallo al código sin ver sus anotaciones.
- No se ha desplegado en Railway ni se ha activado ninguna credencial de producción.

## Bloqueos concretos para cerrar

1. Revisar en GitHub las anotaciones de los checks fallidos de PR #123 y PR #4; no fusionar mientras sigan rojos.
2. Configurar en los servicios reales los secretos compartidos HMAC y el token de Multifunción, sin enviarlos por chat ni guardarlos en Git.
3. Montar almacenamiento persistente /data y mantener una sola réplica mientras SQLite sea la base de datos.
4. Probar el roundtrip remoto de ambos puentes y el webhook real del PSP; conciliar cobros con la cuenta bancaria.
5. Implementar los 52 handlers restantes o sus adaptadores oficiales y superar los gates de producción.

**Conclusión:** el núcleo ejecutable de Multitareas está construido y probado localmente. El sistema completo autónomo 24/7 y los puentes remotos aún no están terminados ni en producción.
