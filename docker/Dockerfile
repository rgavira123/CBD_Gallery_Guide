FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && \
    apt-get install -y libpq-dev gcc netcat-openbsd && \
    rm -rf /var/lib/apt/lists/*

# … resto de tu Dockerfile …


# Copiar los archivos necesarios
COPY ../requirements.txt /app/requirements.txt

# Instalar dependencias de Python
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el resto del proyectoss
COPY .. /app

# Hacer ejecutable el script de entrada
RUN chmod +x docker/entrypoint.sh

# Configurar el script de entrada
ENTRYPOINT ["docker/entrypoint.sh"]