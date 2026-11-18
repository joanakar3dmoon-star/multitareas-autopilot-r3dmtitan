# Despliegue del servicio API + worker

El contenedor ejecuta un único proceso HTTP y un worker thread que comparten una base SQLite local. Es un servicio de una sola réplica; no escalar horizontalmente ni compartir el fichero SQLite entre instancias.

## Endpoints

- GET /health — health check básico de SQLite.
- GET /api/coverage — requiere X-Multitareas-Token; devuelve catálogo y recuento de handlers.
- POST /api/tasks — requiere token; encola una tarea y devuelve HTTP 202.
- GET /api/tasks/{task_id} — requiere token; consulta estado y resultado.
- POST /api/plans — requiere token; solicita una propuesta al planificador. La propuesta no crea ni ejecuta tareas.

## Variables necesarias

- MULTITAREAS_API_TOKEN: secreto aleatorio de al menos 32 caracteres. No se guarda en Git.
- MULTITAREAS_DATABASE: ruta del fichero SQLite persistente, por ejemplo /data/multitareas.db.
- PORT: puerto HTTP que entrega el proveedor.
- AI_PROVIDER=ollama y AI_REMOTE_ENABLED=0 por defecto. El planificador necesita un modelo Ollama disponible; no se finge una respuesta si no está instalado.
- CEREBRO_BASE_URL, CEREBRO_SHARED_SECRET y CEREBRO_EVENTS_PATH: dejar vacíos hasta disponer del receptor real.
- MULTIFUNCION_BRIDGE_ENABLED=0: no activar hasta que la API del otro repositorio esté integrada y desplegada.
- MARKETPLACE_ADAPTERS_ENABLED=0 y permisos de salida de dinero en 0.

## Docker local

```sh
docker build -t multitareas-autopilot .
docker run --rm -p 8000:8000 \
  -e MULTITAREAS_API_TOKEN="$MULTITAREAS_API_TOKEN" \
  -e MULTITAREAS_DATABASE=/data/multitareas.db \
  -v multitareas-data:/data \
  multitareas-autopilot
```

La plataforma debe terminar TLS delante del contenedor. El endpoint /health no revela estado financiero ni secretos. Las demás rutas exigen el token.

## Gates aún pendientes

La imagen y API no equivalen a despliegue. Antes de producción: volumen persistente real, token en secret manager, prueba de restauración, modelo IA disponible, endpoints externos confirmados, sandbox de proveedores, conciliación PSP/banco y prueba prolongada. Los tests loopback solo validan el contrato local simulado.
