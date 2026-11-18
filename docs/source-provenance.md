# Procedencia y límites del primer traslado

El scaffold inicial se trasladó desde el subdirectorio multitareas-autopilot-r3dmtitan/ de joanakar3dmoon-star/quasar-autopilot, rama backup/multitareas-autopilot-pr121-20261118, commit fuente 6ecf5766628c3b2cb27246ffb213ec48ac16d7ed (PR #121).

Se trasladaron únicamente los archivos del módulo dedicado. No se copió el árbol raíz de QUASAR ni sus otros negocios, workers, finanzas, frontend, secretos o despliegues. La copia de recuperación y el PR fuente se conservan hasta validar completamente la migración.

Desde el traslado se han añadido en main el runtime SQLite, scheduler opt-in, adaptador de IA acotado y controles de permisos financieros. Estos cambios son posteriores al scaffold original y no forman parte del PR fuente #121.

La presencia de código no demuestra integración operativa, autonomía completa ni producción. Las conexiones externas requieren auditoría, credenciales gestionadas fuera de Git, contratos y pruebas específicas.
