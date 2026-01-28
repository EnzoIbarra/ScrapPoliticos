---
description: Estrategias y heurísticas para construir scrapers robustos
---

# Skill: Scraping Robusto

## Cuándo usar

- Al crear un nuevo scraper para municipios
- Al detectar problemas de extracción
- Al implementar fallbacks

---

## Estrategia General

### 1. Siempre empezar con HTTP básico

```python
# Primero intentar con requests + BeautifulSoup
response = requests.get(url)
html = response.text
```

**Por qué:** Es rápido (~1-2s) y funciona en el 80% de casos

### 2. Detectar si JavaScript es necesario

**Síntomas de JavaScript rendering:**

- HTML muy pequeño (<5KB) para una página completa
- Contenedores vacíos: `<div id="content"></div>`
- Spinners/loaders: `<div class="loading">...</div>`
- Atributos dinámicos: `data-src`, `data-lazy`, `ng-*`, `v-*`
- Frameworks detectables: React, Vue, Angular

**Código de detección:**

```python
def requiere_javascript(html: str) -> bool:
    # HTML muy pequeño
    if len(html) < 5000:
        return True

    # Contenedores vacíos comunes
    if '<div id="content"></div>' in html:
        return True

    # Frameworks JS
    frameworks = ['react', 'vue', 'angular', 'ng-app']
    return any(fw in html.lower() for fw in frameworks)
```

### 3. Usar Playwright solo si necesario

**Cuándo:**

- Detección automática indica JavaScript
- Contenido lazy-load con scroll
- SPA (Single Page Applications)

**Costo:** ~8-10s por página vs 1-2s (HTTP)

### 4. OCR como último recurso

**Cuándo:**

- Ratio imágenes/texto muy alto (>3:1)
- Imágenes con alt/title que sugieren contenido (`cargo`, `nombre`)
- Tablas/listas renderizadas como imágenes

**Precisión:** 80-95% (depende de calidad imagen)

---

## Heurísticas de Detección

### JavaScript Necesario

```python
def detectar_javascript(url: str, html: str) -> int:
    """Retorna score 0-100 de probabilidad de necesitar JS"""
    score = 0

    # HTML vacío/muy pequeño
    if len(html) < 5000:
        score += 40

    # Contenedores vacíos
    if html.count('<div></div>') > 3:
        score += 20

    # Loading spinners
    if 'spinner' in html.lower() or 'loading' in html.lower():
        score += 15

    # Frameworks
    frameworks = {
        'react': 20,
        'vue': 20,
        'angular': 20,
        'ng-app': 25,
        'data-react': 25
    }
    for fw, points in frameworks.items():
        if fw in html.lower():
            score += points
            break

    return min(score, 100)
```

### Contenido en Imágenes (OCR)

```python
def detectar_ocr(html: str) -> int:
    """Retorna score 0-100 de probabilidad de necesitar OCR"""
    from bs4 import BeautifulSoup

    soup = BeautifulSoup(html, 'html.parser')

    # Contar imágenes vs texto
    imagenes = len(soup.find_all('img'))
    texto = len(soup.get_text(strip=True))

    score = 0

    # Ratio alto de imágenes
    if imagenes > 0 and texto > 0:
        ratio = imagenes / (texto / 1000)  # imágenes por cada 1000 caracteres
        if ratio > 3:
            score += 40

    # Imágenes con keywords relevantes en alt/title
    keywords = ['cargo', 'nombre', 'concejal', 'telefono', 'email']
    for img in soup.find_all('img'):
        alt = (img.get('alt') or '').lower()
        title = (img.get('title') or '').lower()
        if any(kw in alt or kw in title for kw in keywords):
            score += 30
            break

    # Tablas/listas como imágenes
    if imagenes > 5 and soup.find_all(['table', 'ul']) == []:
        score += 20

    return min(score, 100)
```

---

## Rutas Alternativas Comunes

### Patrones de URLs

Los municipios suelen usar estas rutas estándar:

```python
RUTAS_COMUNES = [
    '/corporacion',
    '/corporacion-municipal',
    '/equipo-gobierno',
    '/equipo-de-gobierno',
    '/grupo-gobierno',
    '/grupo-de-gobierno',
    '/concejales',
    '/concejalias',
    '/organigrama',
    '/estructura',
    '/gobierno/concejales',
    '/ayuntamiento/corporacion',
    '/ayuntamiento/equipo',
    '/contacto',
    '/contactos',
    '/directorio',
    '/telefonos',
    '/regimen-interior'
]
```

### Auto-generación de Rutas

```python
def generar_rutas_alternativas(domain: str) -> List[str]:
    """Genera rutas alternativas a probar"""
    base_url = f"https://{domain}"

    rutas = []
    for ruta in RUTAS_COMUNES:
        rutas.append(urljoin(base_url, ruta))

    return rutas
```

---

## Sistema de Fallbacks

### Orden de Intentos

```python
def scrape_con_fallbacks(municipality: Dict) -> Dict:
    """Intenta múltiples estrategias hasta tener éxito"""

    estrategias = [
        ('http_base', lambda: http_scraper.scrape(url_base)),
        ('http_alternativas', lambda: probar_rutas_alternativas()),
        ('javascript_base', lambda: playwright_scraper.scrape(url_base)),
        ('javascript_alternativas', lambda: playwright_con_rutas()),
        ('ocr', lambda: ocr_scraper.scrape(urls_con_imagenes))
    ]

    for nombre, estrategia in estrategias:
        try:
            logger.info(f"Intentando estrategia: {nombre}")
            result = estrategia()

            if result['status'] == 'success' and len(result['data']) > 0:
                logger.info(f"✅ Éxito con estrategia: {nombre}")
                return result

        except Exception as e:
            logger.warning(f"❌ Falló {nombre}: {e}")
            continue

    return {'status': 'error', 'error': 'Todas las estrategias fallaron'}
```

---

## Ejemplos Reales

### Caso 1: Santa Cruz de la Palma

**Problema:** Contenido dinámico con JavaScript  
**Síntomas:**

- Hash en URL: `#concejalia`
- HTML inicial pequeño
- Contenido carga después

**Solución:** Playwright con scroll

```python
config = {
    'scroll': True,
    'scroll_delay': 2,
    'wait_selector': None
}
result = playwright_scraper.scrape(url, config)
```

### Caso 2: Puntallana

**Problema:** Información en imágenes  
**Síntomas:**

- Múltiples `<img>` con nombres/cargos
- Alt text: "CORPORACION MUNICIPAL", "TELEFONOS"

**Solución:** OCR

```python
config = {
    'urls': [
        'https://puntallana.es/grupo-de-gobierno/',
        'https://puntallana.es/telefonos-interes/'
    ],
    'image_selectors': ['img']
}
result = ocr_scraper.scrape(municipality, config)
```

### Caso 3: Agaete

**Problema:** URL incorrecta + información en ruta alternativa  
**Síntomas:**

- URL base no tiene datos
- Datos en `/ayuntamiento/corporacion-municipal`

**Solución:** Rutas alternativas

```python
rutas_alternativas = [
    '/ayuntamiento/corporacion-municipal',
    '/ayuntamiento/equipo-de-gobierno'
]

for ruta in rutas_alternativas:
    url = urljoin(base_url, ruta)
    result = http_scraper.scrape(url)
    if result['status'] == 'success':
        break
```

---

## Debugging

### Problema: No se extrae nada

**Checklist:**

1. ¿La URL es correcta? Verificar manualmente en browser
2. ¿El HTML tiene contenido? Ver `len(html)`
3. ¿Es JavaScript? Usar `detectar_javascript()`
4. ¿Hay rutas alternativas? Probar `RUTAS_COMUNES`
5. ¿Es OCR? Ver ratio imágenes/texto

### Problema: Datos incompletos

**Checklist:**

1. ¿Llegó al `max_pages`? Aumentar límite
2. ¿Hay paginación? Detectar links `next`, `siguiente`
3. ¿Keywords correctas? Agregar variantes
4. ¿Scroll necesario? (lazy-load) → Playwright

### Problema: Scraper muy lento

**Optimizaciones:**

1. Reducir `max_pages` si no necesario
2. Usar HTTP en lugar de Playwright cuando sea posible
3. Implementar cache de resultados
4. Batch multiple requests

---

## Referencias

- `worker.py` - Scraper HTTP actual
- `worker_advanced.py` - Playwright implementation
- `ocr_processor.py` - OCR implementation
- `special_cases.json` - Casos configurados manualmente
