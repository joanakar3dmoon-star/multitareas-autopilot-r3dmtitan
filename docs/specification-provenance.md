# Procedencia de la especificación funcional

El catálogo y las especificaciones declarativas de ALPHA, BETA y GAMMA se adaptaron desde la rama integracion/tres-pulpos-upgrade, PR #4, del repositorio privado joanakar3dmoon-star/superagente-autopilot-multifuncion (commit de referencia 1d6c99560aeaaf17efceef62e8accea712e3d83c).

Se copiaron únicamente:
- catálogo funcional JSON;
- especificaciones de tareas JSON;
- arquitectura y contratos funcionales;
- documentación de bloques operativos y matriz de cobertura de origen.

No se copiaron workers, runtime, bases de datos, secretos, despliegues ni configuración de ese proyecto. El código de Multitareas sigue siendo independiente y no comparte su base de datos.

La especificación contiene 81 tareas declarativas: ALPHA 37, BETA 29 y GAMMA 15. La declaración de una tarea no significa que tenga handler, proveedor, datos actuales o ejecución externa. La matriz docs/coverage-matrix.md refleja el estado real de este repositorio.
