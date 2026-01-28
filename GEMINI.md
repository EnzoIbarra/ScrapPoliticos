# Reglas del Proyecto: ScrapPoliticos

Sistema robusto de scraping de datos municipales con detección automática y fallbacks inteligentes.

---

## 🏗️ Arquitectura

### Vertical Slice Architecture

- Cada scraper es **autónomo** y completo
- Funcionalidad organizada por **feature**, no por capa técnica
- **Single Responsibility**: Un módulo = Una responsabilidad clara

### Estructura de Carpetas

```
/core        → Lógica central reutilizable
/scrapers    → Estrategias de scraping (HTTP, JS, OCR)
/config      → Configuraciones centralizadas
/docs        → Documentación técnica
/tests       → Tests organizados por módulo
/.agent      → Skills y workflows para IA
```

---

## 🐳 Entorno Docker (OBLIGATORIO)

### Regla de Oro

**TODO el código se ejecuta mediante Docker.** No existe ejecución local de Python.

### Comandos Estándar

```bash
# Construcción
make build

# Ejecución
make up

# Tests
make test

# Shell interactiva
make shell

# Ver todos los comandos
make help
```

### Prohibiciones Absolutas

❌ **NUNCA** sugerir o usar:

- `pip install -r requirements.txt`
- `python main.py`
- `playwright install chromium`

✅ **SIEMPRE** usar:

- `make build`
- `make up`
- `docker-compose run --rm scraper python script.py`

### Persistencia

Los siguientes directorios están montados como volúmenes:

- `data/`: Resultados del scraping
- `logs/`: Logs de ejecución
- `.env`: Variables de entorno

---

## 💻 Código Python

### Estilo

- **PEP 8** estrictamente (sin excepciones)
- **Type hints** obligatorios en funciones públicas
- **Docstrings** en español formato Google
- **4 espacios** para indentación

### Nomenclatura

```python
# Variables y funciones: snake_case (español)
municipio_actual = "Agaete"
def extraer_concejales(html: str) -> List[Dict]:
    pass

# Clases: PascalCase (inglés)
class HTTPScraper:
    pass

# Constantes: UPPER_CASE
MAX_REINTENTOS = 3
TIMEOUT_SEGUNDOS = 30

# Archivos: lowercase_guiones
# ✅ http_scraper.py
# ❌ HTTPScraper.py
```

### Imports (Orden Estricto)

```python
# 1. Built-in
import os
import json
from typing import List, Dict

# 2. Third-party
import requests
from bs4 import BeautifulSoup

# 3. Local
from core.validator import DataValidator
from scrapers.base import BaseScraper
```

---

## 🛡️ Manejo de Errores

### Reglas Obligatorias

❌ **PROHIBIDO** - Try-catch vacío o genérico

```python
# ❌ MAL
try:
    result = scrape()
except:
    pass
```

✅ **CORRECTO** - Logging + retry + fallback

```python
# ✅ BIEN
try:
    result = scrape()
except RequestException as e:
    logger.error(f"Error HTTP: {e}", exc_info=True)
    return retry_with_fallback()
```

### Sistema de Logging

```python
from core.logger import get_logger

logger = get_logger(__name__)

# Niveles:
logger.debug("Detalle de implementación")
logger.info("Operación exitosa")
logger.warning("Problema recoverable")
logger.error("Error que requiere atención")
```

### Retry con Backoff

```python
from core.retry_handler import retry_with_fallback

@retry_with_fallback(max_retries=3, backoff=2)
def fetch_data(url: str) -> str:
    # Se reintenta automáticamente 3 veces con backoff exponencial
    return requests.get(url).text
```

---

## ⚙️ Configuración

### Reglas de Oro

1. **TODO configurable** vía archivos en `/config`
2. **NUNCA valores hardcoded** en el código
3. **Secretos SOLO** en `.env` (nunca en git)
4. **Validar configs** al inicio de la app

### Ejemplo

```python
# ❌ MAL - Hardcoded
models = ["meta-llama/llama-3.3-70b-instruct:free"]

# ✅ BIEN - Configuración externa
from config import load_models_config
models = load_models_config()
```

---

## 🧪 Testing

### Cobertura Obligatoria

- **Test unitario** para cada scraper
- **Test de integración** end-to-end
- **Coverage mínimo**: 70%

### Mocks para APIs Externas

```python
from unittest.mock import patch

@patch('requests.get')
def test_http_scraper(mock_get):
    mock_get.return_value.text = "<html>...</html>"
    result = http_scraper.scrape(municipality)
    assert result['status'] == 'success'
```

---

## 📝 Commits

### Conventional Commits (Obligatorio)

```bash
# Formato:
<tipo>: <descripción>

# Tipos permitidos:
feat:     # Nueva funcionalidad
fix:      # Corrección de bug
refactor: # Refactorización sin cambio funcional
docs:     # Cambios en documentación
test:     # Agregar o modificar tests
chore:    # Mantenimiento (deps, configs)

# Ejemplos:
feat: agregar detector automático de JavaScript
fix: corregir validación de emails con dominios especiales
refactor: extraer lógica de retry a módulo independiente
docs: documentar heurísticas de detección de OCR
```

### Mensajes en Español

```bash
✅ feat: implementar scraper con OCR para Puntallana
❌ feat: implement OCR scraper for Puntallana
```

### Atomic Commits

- **Un commit = Un cambio lógico**
- No mezclar refactor con nuevas features
- Tests en el mismo commit que el código que testean

---

## 📚 Documentación

### README.md (Raíz)

- **Conciso**: Solo overview, quick start, links
- **Máximo 100 líneas**
- Links a `/docs` para detalles

### Docs Detallados en `/docs`

- `architecture.md` - Diseño del sistema
- `setup.md` - Instalación paso a paso
- `troubleshooting.md` - Problemas comunes
- `api.md` - API de módulos públicos

### Docstrings (Funciones Públicas)

```python
def extraer_concejales(html: str, url: str) -> List[Dict]:
    """Extrae información de concejales desde HTML.

    Args:
        html: Contenido HTML de la página
        url: URL de origen para trazabilidad

    Returns:
        Lista de diccionarios con datos de concejales. Cada dict contiene:
        - nombre: str
        - cargo: str
        - partido: str (opcional)
        - email: str (opcional)

    Raises:
        ValueError: Si el HTML está vacío o es inválido
    """
    pass
```

### Inline Comments

- **Solo para código complejo** (algoritmos, heurísticas)
- **No** comentar lo obvio
- **Explicar el POR QUÉ**, no el QUÉ

```python
# ❌ MAL
i += 1  # Incrementa i

# ✅ BIEN
# Usar backoff exponencial para evitar rate limits de la API
wait_time = 2 ** intento
```

---

## 🤖 Skills para IA (Gemini)

### Ubicación

`.agent/skills/<nombre>.md`

### Formato

```markdown
---
description: Descripción corta del skill
---

# Skill: <Nombre>

## Cuándo usar

...

## Heurísticas

...

## Ejemplos

...
```

### Skills Obligatorios

- `scraping.md` - Estrategias de scraping
- `data-validation.md` - Validación de datos
- `debugging.md` - Debug common issues

---

## 🚨 Reglas Críticas (NUNCA violar)

### 🔴 Seguridad

- ❌ **NUNCA** commitear `.env` o archivos con secretos
- ❌ **NUNCA** loggear API keys completas
- ✅ **SIEMPRE** usar `os.getenv()` para secretos

### 🔴 Performance

- ❌ **NUNCA** hacer requests síncronos en loop (usar batch)
- ❌ **NUNCA** cargar archivos completos en memoria si >10MB
- ✅ **SIEMPRE** usar timeouts en requests

### 🔴 Robustez

- ❌ **NUNCA** asumir que una request va a funcionar
- ❌ **NUNCA** silenciar errores con `pass`
- ✅ **SIEMPRE** validar datos antes de guardar

### 🔴 Mantenibilidad

- ❌ **NUNCA** hacer funciones >50 líneas (extraer submétodos)
- ❌ **NUNCA** duplicar código (DRY)
- ✅ **SIEMPRE** refactorizar antes de agregar features

---

## 📊 Métricas de Calidad

### Code Quality

- **Pylint score**: ≥ 8.0/10
- **Coverage**: ≥ 70%
- **Complejidad ciclomática**: ≤ 10 por función

### Performance

- **Tiempo por municipio**: < 2 min (promedio)
- **Memory usage**: < 500MB
- **Error rate**: < 5%

---

## 🔄 Workflow de Desarrollo

1. **Crear branch** desde `main`

   ```bash
   git checkout -b feat/detector-automatico
   ```

2. **Desarrollar** siguiendo estas reglas

3. **Testear** localmente

   ```bash
   pytest tests/
   pylint core/ scrapers/
   ```

4. **Commit** siguiendo Conventional Commits

5. **Push** y crear PR

6. **Code review** obligatorio

7. **Merge** solo si tests pasan

---

## 📖 Referencias

- [PEP 8](https://pep8.org/)
- [Conventional Commits](https://www.conventionalcommits.org/)
- [Google Docstring Style](https://google.github.io/styleguide/pyguide.html#38-comments-and-docstrings)

---

**Última actualización**: 2026-01-27
**Versión**: 1.0.0
