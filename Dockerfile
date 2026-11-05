# Imagen de la aplicación: la misma para Docker Compose, CI y el despliegue en Render.
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8000

WORKDIR /app
COPY requirements.txt requirements-dev.txt ./
ARG INSTALAR_DEV=false
RUN pip install --no-cache-dir -r requirements.txt \
    && if [ "$INSTALAR_DEV" = "true" ]; then pip install --no-cache-dir -r requirements-dev.txt; fi

COPY src ./src
COPY datos ./datos
COPY tests ./tests
COPY scripts ./scripts
COPY pyproject.toml ./

RUN useradd --create-home edutech && chown -R edutech /app
USER edutech

EXPOSE 8000
# Render y otras plataformas indican el puerto en la variable PORT.
CMD ["sh", "-c", "uvicorn src.api.main:app --host 0.0.0.0 --port ${PORT}"]
