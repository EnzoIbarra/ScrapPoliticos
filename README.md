# ScrapPoliticos 🏛️

Sistema robusto de scraping de datos de concejales municipales de Canarias con detección automática de estrategias y fallbacks inteligentes.

## 🚀 Inicio Rápido

### Requisitos Previos

- [Docker](https://docs.docker.com/get-docker/)
- [Docker Compose](https://docs.docker.com/compose/install/)

### Ejecución

1. **Configuración:**
   Crea un archivo `.env` basado en `.env.example` y añade tu `OPENROUTER_API_KEY`.

2. **Construir imagen:**

   ```bash
   make build
   # o: docker-compose build
   ```

3. **Ejecutar scraper:**

   ```bash
   make up
   # o: docker-compose up scraper
   ```

4. **Ver comandos disponibles:**
   ```bash
   make help
   ```

## 🏗️ Arquitectura (Vertical Slice)

El sistema utiliza tres estrategias de scraping coordinadas:

- **HTTP Scraper**: Estrategia por defecto para sitios estáticos (Rápida).
- **JavaScript Scraper**: Usa Playwright para sitios con contenido dinámico.
- **OCR Scraper**: Usa Tesseract para extraer información de imágenes.

Para más detalles, consulta [docs/architecture.md](docs/architecture.md).

## 📁 Estructura del Proyecto

- `/config`: Archivos de configuración JSON (dominios, rutas, modelos).
- `/core`: Lógica central (IA, validación, reintentos).
- `/scrapers`: Diferentes motores de scraping.
- `/docs`: Documentación técnica detallada.
- `/tests`: Scripts de validación y pruebas.
- `/scripts`: Utilidades adicionales.

## 🛡️ Robustez

- **Detección Automática**: Selecciona la mejor estrategia según el municipio.
- **Reintentos**: Sistema de reintentos con backoff exponencial.
- **Validación de Datos**: Limpieza automática de nombres, emails y cargos.

## 📜 Reglas de Desarrollo

Consulta [GEMINI.md](GEMINI.md) para conocer los estándares de código, arquitectura y commits seguidos en este proyecto.

---

**Versión**: 2.0.0 | **Arquitectura**: Vertical Slice
