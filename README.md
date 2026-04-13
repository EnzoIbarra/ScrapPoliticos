# ScrapPoliticos | Intelligent Scraping & Data Extraction System

> [!IMPORTANT]
> **Project Context:** This system was developed as part of a specialized data extraction initiative focused on Spanish municipalities. It is uploaded here to demonstrate advanced Python capabilities, infrastructure management with Docker, and automated ETL (Extract, Transform, Load) processes.
> 
> **Contexto del Proyecto:** Este sistema fue desarrollado como parte de una iniciativa especializada de extracción de datos en municipios españoles. Se publica para demostrar habilidades avanzadas en Python, gestión de infraestructura con Docker y procesos automatizados de ETL.

---

## 🇺🇸 English Version

### 🚀 Overview
An advanced, multi-layered scraping system designed to extract contact information for political officials (Mayors and Councilors). The engine is built with a **Waterfall Architecture**, automatically switching between strategies to bypass blocks and handle both static and dynamic (SPA) websites.

### 🛠 Tech Stack
* **Language:** Python 3.x.
* **Scraping Engines:** Playwright (Chromium), Requests, BeautifulSoup4.
* **Infrastructure:** Docker & Docker Compose.
* **Network & Privacy:** Tor Network integration for IP rotation.
* **Data Processing:** Pandas (Excel/JSON export), Regex-based AI for email de-obfuscation.

### 🎯 Key Engineering Features
* **Waterfall Strategy Engine:** A 3-level fallback system:
    1. **Level 1 (Tor):** Total anonymity for static HTML.
    2. **Level 2 (Direct IP):** High-speed extraction for non-restricted sites.
    3. **Level 3 (Playwright):** Real browser automation for React/Angular/Vue sites.
* **Intelligent Filtering:** Strict whitelist logic to isolate political roles, actively discarding administrative or technical staff.
* **Hybrid Email Recovery:** Combines regex patterns with AI-driven logic to recover hidden or obfuscated `mailto:` links.
* **On-Boarding Ready Code:** The codebase is **exhaustively commented** and documented. This was a strategic requirement to ensure a smooth hand-off to new developers, minimizing the learning curve for system maintenance.
* **Automated Toolset:** Includes custom scripts for data cleaning ("Garbage Collector"), email diagnostics, and corporate Excel reporting.

---

## 🇦🇷 Versión en Español

### 🚀 Resumen
Sistema avanzado de scraping multicapa diseñado para la extracción de datos de contacto de cargos políticos. El motor utiliza una **Arquitectura en Cascada ("The Waterfall")**, alternando automáticamente entre estrategias para evadir bloqueos y procesar sitios tanto estáticos como dinámicos (SPA).

### 🛠 Stack Tecnológico
* **Lenguaje:** Python 3.x.
* **Motores de Scraping:** Playwright, Requests, BeautifulSoup4.
* **Infraestructura:** Docker & Docker Compose.
* **Red y Privacidad:** Integración con la red Tor para rotación de IPs.
* **Procesamiento:** Pandas (Excel/JSON), Lógica de IA con Regex para desofuscación de emails.

### 🎯 Características de Ingeniería
* **Motor de Estrategia en Cascada:** Sistema de tres niveles:
    1. **Nivel 1 (Tor):** Anonimato total para HTML estático.
    2. **Nivel 2 (IP Directa):** Extracción veloz para sitios sin restricciones.
    3. **Nivel 3 (Playwright):** Automatización de navegador real para sitios en React/Angular/Vue.
* **Filtrado Inteligente:** Lógica de lista blanca estricta para aislar cargos políticos, descartando personal técnico o administrativo.
* **Código para Nuevos Ingresantes:** Todo el código fuente cuenta con **comentarios exhaustivos y documentación interna**. Este fue un requerimiento estratégico para facilitar el traspaso a nuevos desarrolladores y reducir la curva de aprendizaje en el mantenimiento del sistema.
* **Herramientas Automatizadas:** Incluye scripts personalizados para limpieza de datos ("Garbage Collector"), diagnóstico de emails y generación de reportes corporativos en Excel.

---

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
