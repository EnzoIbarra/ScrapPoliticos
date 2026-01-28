# Config - Configuración del Sistema

Este directorio contiene todos los archivos de configuración del sistema de scraping.

## 📁 Archivos de Configuración

### `canarias_municipios.json`

**Propósito:** Lista completa de municipios de Canarias con sus URLs.

**Formato:**

```json
[
  {
    "municipio": "Agaete",
    "url": "www.agaete.es",
    "isla": "Gran Canaria"
  }
]
```

**Cómo agregar un municipio:**

1. Agregar entrada al array JSON
2. Incluir campos: `municipio`, `url`, `isla`
3. Validar formato con `make validate`

---

### `municipality_strategies.json`

**Propósito:** Mapeo de municipios a estrategias de scraping específicas.

**Formato:**

```json
{
  "Puntallana": "ocr",
  "Las Palmas": "javascript",
  "Agaete": "http"
}
```

**Estrategias disponibles:**

- `http`: Scraping estático (por defecto)
- `javascript`: Scraping con Playwright
- `ocr`: Extracción desde imágenes

---

### `ai_models.json`

**Propósito:** Configuración de modelos de IA para extracción.

**Formato:**

```json
{
  "models": [
    "meta-llama/llama-3.3-70b-instruct:free",
    "google/gemini-2.0-flash-exp:free"
  ],
  "max_retries": 2,
  "timeout": 30
}
```

**Campos:**

- `models`: Lista de modelos en orden de prioridad (fallback automático)
- `max_retries`: Número de reintentos por modelo
- `timeout`: Timeout en segundos para cada request

---

### `scraping_paths.json`

**Propósito:** Rutas y selectores CSS para extracción de datos.

**Formato:**

```json
{
  "default": {
    "concejales_section": ["#concejales", ".gobierno", ".corporacion"],
    "nombre_selector": [".nombre", "h3", ".councilor-name"],
    "cargo_selector": [".cargo", ".position", ".role"]
  },
  "custom": {
    "Las Palmas": {
      "concejales_section": ["#gobierno-municipal"]
    }
  }
}
```

**Uso:**

- `default`: Selectores genéricos probados en múltiples sitios
- `custom`: Selectores específicos por municipio

---

## 🔧 Validación de Configuración

Antes de ejecutar el scraper, valida la configuración:

```bash
make validate
# o: docker-compose run --rm scraper python tests/validate_config.py
```

## 📝 Buenas Prácticas

1. **No hardcodear valores:** Toda configuración debe estar en estos archivos
2. **Validar JSON:** Usar herramientas como `jsonlint` antes de commitear
3. **Documentar cambios:** Actualizar este README al agregar nuevos archivos
4. **Versionado:** Mantener backups de configuraciones críticas

## 🔗 Referencias

- [Documentación de Arquitectura](../docs/architecture.md)
- [Guía de Scrapers](../scrapers/README.md)
