FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    MULTITAREAS_DATABASE=/data/multitareas.db

WORKDIR /app
RUN useradd --create-home --uid 10001 appuser \
    && mkdir -p /data \
    && chown -R appuser:appuser /app /data

COPY --chown=appuser:appuser . /app
USER appuser

EXPOSE 8000
VOLUME ["/data"]
HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 \
  CMD python -c "import os,urllib.request; p=os.getenv('PORT','8000'); urllib.request.urlopen('http://127.0.0.1:'+p+'/health', timeout=3).read()"

CMD ["python", "run_server.py"]
