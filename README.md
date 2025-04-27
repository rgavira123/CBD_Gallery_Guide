# Gallery Guide

Bienvenido a Gallery Guide, una plataforma web para la planificación de rutas personalizadas en museos.

Actualmente, Gallery Guide se encuentra en fase de desarrollo. A continuación, se presentan las dos formas de instalar y ejecutar el sistema.

## Instalación

### 1. Instalación mediante Docker (Recomendada)

Esta es la forma más sencilla para levantar la aplicación. Asegúrate de tener Docker encendido en tu máquina.

#### Pasos:

1. Clonar el repositorio oficial:

```bash
git clone https://github.com/rgavira123/CBD_Gallery_Guide.git
```

2. Acceder a la carpeta de Docker:

```bash
cd docker/
```

3. Copiar el archivo de configuración:

```bash
cp .env.example .env
```

4. Construir y levantar los contenedores:

```bash
docker-compose up --build
```

Esto construirá las imágenes necesarias, levantará PostgreSQL, Neo4j y el contenedor Django, aplicará migraciones y ejecutará automáticamente el script `populate_db` para poblar la base de datos.

5. Acceder a la aplicación desde el navegador:

```bash
http://localhost:8000
```

Para apagar y eliminar los contenedores en caso de fallo o para limpiar el sistema:

```bash
docker-compose down
```

⚠️ **Importante**:  
En caso de error relacionado con el script `entrypoint.sh` (por ejemplo, `no such file or directory`), asegúrate en Visual Studio Code de cambiar la configuración de saltos de línea de **CRLF** a **LF**:

1. Abre el archivo `docker/entrypoint.sh` en VSCode.
2. En la esquina inferior derecha, haz clic donde pone `CRLF`.
3. Selecciona `LF`.
4. Guarda el archivo.

De esta forma el contenedor podrá ejecutar correctamente el script de entrada.


---

### 2. Instalación Local Tradicional

Requiere configuración manual de dependencias y bases de datos.

#### Pasos:

1. Clonar el repositorio:

```bash
git clone https://github.com/rgavira123/CBD_Gallery_Guide.git
```

2. Crear un entorno virtual:

```bash
python -m venv .venv
```

3. Activar el entorno virtual:

- En Windows:

```bash
.venv\Scripts\activate
```

- En Linux/MacOS:

```bash
source .venv/bin/activate
```

4. Instalar dependencias:

```bash
pip install -r requirements.txt
```

5. Configurar las bases de datos manualmente:

- Crear una base de datos PostgreSQL para los usuarios.
- Tener Neo4j ejecutándose localmente.
- Configurar el archivo `.env` basado en el `.env.example` proporcionado (fuera de Docker).

6. Poblar la base de datos:

```bash
cd gallery_guide
python manage.py populate_db
```

7. Ejecutar el servidor de desarrollo:

```bash
python manage.py runserver
```

8. Acceder a la aplicación desde el navegador:

```bash
http://localhost:8000
```

---

## Notas Importantes

- Se recomienda utilizar Docker para garantizar una configuración automática y sin conflictos.
- El despliegue local requiere experiencia previa en configuración de entornos Python y bases de datos.
- Es necesario tener Docker Desktop y Docker Compose instalados si se opta por la vía recomendada.

---

¡Disfruta explorando el arte con Gallery Guide!
