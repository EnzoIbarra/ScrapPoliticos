# Core - Lógica Central

Este directorio contiene los módulos centrales reutilizables del sistema de scraping.

## 📁 Módulos

### `ai_extractor.py`

Extracción de datos usando modelos de IA (OpenRouter).

**Funciones principales:**

- `extract_with_ai(html: str, url: str) -> List[Dict]`: Extrae información de concejales usando IA
- Maneja múltiples modelos con fallback automático
- Sistema de reintentos con backoff exponencial

### `data_validator.py`

Validación y limpieza de datos extraídos.

**Funciones principales:**

- `validate_email(email: str) -> bool`: Valida formato de emails
- `clean_name(name: str) -> str`: Normaliza nombres
- `validate_councilor_data(data: Dict) -> Dict`: Valida y limpia datos completos

### `logger.py`

Sistema de logging centralizado.

**Funciones principales:**

- `get_logger(name: str) -> Logger`: Obtiene logger configurado
- Logs a archivo (`logs/scraper.log`) y consola
- Formato estructurado con timestamps

### `retry_handler.py`

Decorador para reintentos con backoff exponencial.

**Funciones principales:**

- `@retry_with_fallback(max_retries=3, backoff=2)`: Decorador para reintentos automáticos
- Maneja errores de red y timeouts
- Logging automático de intentos fallidos

## 🔧 Uso

Todos los módulos están diseñados para ser importados y usados por los scrapers:

```python
from core.ai_extractor import extract_with_ai
from core.data_validator import validate_councilor_data
from core.logger import get_logger
from core.retry_handler import retry_with_fallback

logger = get_logger(__name__)

@retry_with_fallback(max_retries=3)
def scrape_municipality(url: str):
    html = fetch_html(url)
    raw_data = extract_with_ai(html, url)
    return [validate_councilor_data(d) for d in raw_data]
```

## 📚 Documentación Adicional

Para más detalles sobre la arquitectura, consulta [docs/architecture.md](../docs/architecture.md).
