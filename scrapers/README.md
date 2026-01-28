# Scrapers - Estrategias de Extracción

Este directorio contiene las diferentes estrategias de scraping implementadas en el sistema.

## 🎯 Estrategias Disponibles

### HTTP Scraper (`http_scraper.py`)

**Cuándo se usa:** Sitios web estáticos con HTML renderizado en el servidor.

**Características:**

- Rápido y eficiente (no requiere navegador)
- Usa `requests` + `BeautifulSoup`
- Estrategia por defecto para la mayoría de municipios

**Ejemplo de uso:**

```python
from scrapers.http_scraper import HTTPScraper

scraper = HTTPScraper()
result = scraper.scrape(municipality_name="Agaete", url="https://www.agaete.es")
```

---

### JavaScript Scraper (`js_scraper.py`)

**Cuándo se usa:** Sitios con contenido dinámico cargado por JavaScript.

**Características:**

- Usa Playwright con Chromium
- Espera a que el contenido se cargue completamente
- Más lento pero maneja SPAs y contenido dinámico

**Ejemplo de uso:**

```python
from scrapers.js_scraper import JSScraper

scraper = JSScraper()
result = scraper.scrape(municipality_name="Las Palmas", url="https://www.laspalmasgc.es")
```

---

### OCR Scraper (`ocr_scraper.py`)

**Cuándo se usa:** Información disponible solo en imágenes o PDFs escaneados.

**Características:**

- Usa Tesseract OCR
- Captura screenshots con Playwright
- Extrae texto de imágenes

**Ejemplo de uso:**

```python
from scrapers.ocr_scraper import OCRScraper

scraper = OCRScraper()
result = scraper.scrape(municipality_name="Puntallana", url="https://www.puntallana.es")
```

---

## 🔄 Detección Automática

El sistema selecciona automáticamente la estrategia adecuada basándose en:

- Configuración en `config/municipality_strategies.json`
- Heurísticas de detección (presencia de frameworks JS, etc.)
- Fallback a estrategias alternativas en caso de fallo

## 📊 Formato de Salida

Todas las estrategias devuelven el mismo formato:

```python
{
    "municipality": "Nombre del Municipio",
    "url": "https://ejemplo.es",
    "status": "success" | "error",
    "method": "HTTP" | "JavaScript" | "OCR",
    "data": [
        {
            "nombre": "Juan Pérez",
            "cargo": "Alcalde",
            "partido": "PP",
            "email": "juan@municipio.es"
        }
    ],
    "error": None | "Mensaje de error"
}
```

## 🛠️ Desarrollo

Para agregar una nueva estrategia:

1. Crear archivo `nueva_estrategia_scraper.py`
2. Heredar de `BaseScraper` (si existe) o implementar método `scrape()`
3. Registrar en `config/municipality_strategies.json`
4. Agregar tests en `tests/`

## 📚 Documentación Adicional

- [Arquitectura del Sistema](../docs/architecture.md)
- [Guía de Configuración](../config/README.md)
