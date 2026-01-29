# ScrapPoliticos 🕵️‍♂️🏛️

Sistema avanzado de scraping para la extracción de datos de contacto de cargos políticos (Alcaldes y Concejales) en municipios de Canarias.

## 🚀 Estado Actual y Arquitectura

### Arquitectura en Cascada ("The Waterfall")

El sistema utiliza un enfoque secuencial para equilibrar privacidad, velocidad y potencia. Para cada municipio, intenta las estrategias en este orden estricto:

1.  **Nivel 1: HTML Estático + Tor (Privacidad)** 🛡️
    - _Objetivo_: Anonimato total.
    - _Método_: Requests HTTP enrutadas por la red Tor.
    - _Uso_: Primera opción por defecto.

2.  **Nivel 2: HTML Estático + IP Directa (Velocidad)** 🚀
    - _Objetivo_: Velocidad y evasión de bloqueos a Tor.
    - _Método_: Requests HTTP estándar desde la IP del contenedor.
    - _Activación_: Se activa automáticamente si el Nivel 1 falla o da timeout.

3.  **Nivel 3: JavaScript Dinámico (Playwright)** ☢️
    - _Objetivo_: Renderizado de sitios complejos (SPAs, React, Angular).
    - _Método_: Navegador Chromium real automatizado.
    - _Activación_: Último recurso si los métodos HTTP fallan.

### Filtrado y Calidad

- **Filtrado Estricto (Whitelist)**: Solo se extraen "Alcalde/sa", "Concejal/a" y "Teniente de Alcalde". Se bloquean activamente departamentos, técnicos y personal administrativo.
- **Recuperación de Emails (Híbrida)**: Combina IA con extracción de Regex `mailto:` para intentar recuperar emails ocultos u ofuscados. (Nota: La tasa de éxito depende fuertemente de la seguridad del sitio web).

## 🛠️ Uso con Docker

Todo el entorno está contenerizado. No necesitas instalar Python ni dependencias locales.

### Comandos de Scraping

```bash
# Iniciar el proceso de scraping completo (Automático)
docker-compose up
```

### Herramientas de Mantenimiento

**1. Limpieza de Datos ("Garbage Collector")**
Elimina registros que no sean cargos políticos estrictos.

```bash
docker-compose run --rm scraper python scripts/clean_data.py
```

**2. Regenerar Excel Corporativo**
Crea el archivo `data/scrapped_data.xlsx` con los datos actuales.

```bash
docker-compose run --rm scraper python scripts/export_excel.py
```

**3. Diagnóstico de Emails**
Verifica cuántos registros tienen email válido.

```bash
docker-compose run --rm scraper python scripts/diagnose.py
```

**4. Enriquecimiento de Emails (Fast-Track)**
Intenta re-escanear _solo_ para buscar emails, saltando la capa Tor para mayor velocidad.

```bash
docker-compose run --rm scraper python scripts/enrich_emails.py
```

## 📂 Estructura del Proyecto

- `core/`: Lógica central (Manager de estrategias, IA, Logs).
- `scrapers/`: Implementaciones específicas (HTTP con/sin Proxy, JS/Playwright).
- `scripts/`: Herramientas de utilidad (Export, Clean, Diagnose).
- `data/`: Almacenamiento de resultados JSON y Excel.
- `config/`: Listas de rutas y configuraciones de modelos.

## ⚠️ Limitaciones Conocidas

- **Cobertura de Emails**: ~4-10%. Muchos ayuntamientos no publican emails directos de concejales, requiriendo contacto vía formulario web.
- **Velocidad**: El uso de Tor (Nivel 1) añade latencia. El script de enriquecimiento usa "Fast-Track" (Nivel 2) para mitigar esto.
