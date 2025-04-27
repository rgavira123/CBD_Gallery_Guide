#!/bin/sh

# Esperar a que PostgreSQL y Neo4j estén listos
echo "Esperando a que PostgreSQL y Neo4j estén listos..."
while ! nc -z postgres 5432; do
  sleep 1
done
while ! nc -z neo4j 7687; do
  sleep 1
done

# Ejecutar migraciones y poblar la base de datos
echo "Aplicando migraciones y poblando la base de datos..."
python gallery_guide/manage.py migrate
python gallery_guide/manage.py populate_db
# Iniciar el servidor de desarrollo
echo "Iniciando el servidor..."
exec python gallery_guide/manage.py runserver 0.0.0.0:8000
#Saltos de linea