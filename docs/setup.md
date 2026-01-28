# Guía de Instalación y Configuración (Docker)

Instrucciones para preparar el entorno de desarrollo y ejecución del scraper usando Docker.

## 📋 Requisitos Previos

- [Docker](https://docs.docker.com/get-docker/) 20.10+
- [Docker Compose](https://docs.docker.com/compose/install/) 1.29+

## 🛠️ Configuración

### 1. Configuración del Entorno

Crea un archivo `.env` en la raíz del proyecto:

```env
OPENROUTER_API_KEY=tu_clave_aqui
```

### 2. Construcción de la Imagen

```bash
make build
# o: docker-compose build
```

Esto instalará automáticamente:

- Python 3.11 y todas las dependencias
- Playwright y Chromium
- Tor para anonimización (opcional)

## 🚀 Ejecución

### Ejecutar el Scraper

```bash
make up
# o: docker-compose up scraper
```

### Ver Logs en Tiempo Real

```bash
make logs
# o: docker-compose logs -f scraper
```

### Acceder a Shell Interactiva

```bash
make shell
# o: docker-compose run --rm scraper /bin/bash
```

## 🔍 Verificación

Para confirmar que el sistema está listo, ejecuta los tests:

```bash
make test
# o: docker-compose run --rm scraper pytest tests/
```

## 📊 Comandos Útiles

Ver todos los comandos disponibles:

```bash
make help
```
