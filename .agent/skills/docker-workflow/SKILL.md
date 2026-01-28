---
description: Guía para trabajar con Docker en el proyecto ScrapPoliticos
---

# Skill: Docker Workflow

## Cuándo usar

Este skill debe aplicarse cuando:

- Se necesita ejecutar cualquier comando del proyecto
- Se está configurando el entorno de desarrollo
- Se están ejecutando tests o validaciones
- Se necesita acceso a shell interactiva

## Regla de Oro

**TODO en este proyecto se ejecuta mediante Docker.** No existe ejecución local de Python.

## Comandos Principales

### Construcción y Ejecución

```bash
# Construir imagen
make build

# Ejecutar scraper (attached)
make up

# Ejecutar scraper (detached)
make up-detached

# Ver logs en tiempo real
make logs

# Detener contenedores
make down
```

### Desarrollo

```bash
# Acceder a shell interactiva
make shell

# Ejecutar tests
make test

# Validar datos extraídos
make validate

# Exportar a Excel
make export
```

### Mantenimiento

```bash
# Limpiar contenedores y volúmenes
make clean

# Limpiar datos generados
make clean-data

# Reconstruir desde cero
make rebuild

# Ver estado de contenedores
make status
```

## Estructura Docker

### Dockerfile

- Imagen base: `python:3.11-slim`
- Incluye: Playwright, Chromium, Tor
- Todas las dependencias se instalan automáticamente

### docker-compose.yml

- Servicio `tor`: Proxy para anonimización
- Servicio `scraper`: Aplicación principal
- Volúmenes: `data/`, `logs/`, `.env`

## Troubleshooting

### Error: "Cannot connect to Docker daemon"

```bash
# Verificar que Docker esté corriendo
docker ps

# En Windows, asegurarse de que Docker Desktop esté iniciado
```

### Error: "Port already in use"

```bash
# Detener contenedores existentes
make down

# Limpiar completamente
make clean
```

### Logs no se muestran

```bash
# Verificar que el contenedor esté corriendo
make status

# Ver logs completos
docker-compose logs scraper
```

### Cambios en código no se reflejan

```bash
# Reconstruir imagen
make rebuild
```

## Heurísticas

### Cuándo reconstruir la imagen

- Cambios en `requirements.txt`
- Cambios en `Dockerfile`
- Cambios en configuración de sistema

### Cuándo NO reconstruir

- Cambios en código Python (se sincronizan automáticamente vía volúmenes)
- Cambios en archivos de configuración JSON
- Cambios en datos

### Persistencia de datos

- `data/`: Resultados del scraping
- `logs/`: Logs de ejecución
- `.env`: Variables de entorno

Estos directorios están montados como volúmenes, por lo que persisten entre ejecuciones.

## Ejemplos de Uso

### Ejecutar scraping completo

```bash
make build  # Primera vez
make up     # Ejecutar
```

### Debugging interactivo

```bash
make shell
# Dentro del contenedor:
python main.py
```

### Validar resultados

```bash
make validate
# Revisar: data/validation_results.json
```

### Ejecutar un script específico

```bash
docker-compose run --rm scraper python scripts/export_excel.py
```

## Integración con Workflows

Todos los workflows del proyecto (`.agent/workflows/*.md`) usan comandos Docker.

**Nunca** sugerir comandos como:

- ❌ `pip install -r requirements.txt`
- ❌ `python main.py`
- ❌ `playwright install`

**Siempre** usar:

- ✅ `make build`
- ✅ `make up`
- ✅ `docker-compose run --rm scraper python script.py`

## Referencias

- [Makefile](../../../Makefile) - Todos los comandos disponibles
- [docker-compose.yml](../../../docker-compose.yml) - Configuración de servicios
- [Dockerfile](../../../Dockerfile) - Definición de imagen
