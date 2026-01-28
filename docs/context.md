# Contexto y Heurísticas del Proyecto

Este documento resume por qué el sistema es complejo y qué problemas resuelve basándose en el análisis de feedback real.

## 🎯 Problemas Recurrentes

Tras analizar los resultados de múltiples ejecuciones, se identificaron tres patrones de fallo principales:

### 1. JavaScript Dinámico (SPAs)

Muchos portales modernos cargan la lista de concejales asíncronamente.

- **Acción:** Usar `JavaScriptScraper` (Playwright).
- **Ejemplo:** Santa Cruz de la Palma.

### 2. Contenido en Imágenes (Falta de Accesibilidad)

Municipios antiguos o con poca inversión técnica suelen publicar el organigrama como imágenes sueltas.

- **Acción:** Usar `OCRScraper` (Tesseract).
- **Ejemplo:** Puntallana.

### 3. Rutas No Estándar

La información no siempre está en la "home". Suele estar en secciones de transparencia u organización.

- **Heurística:** Buscar en rutas alternativas conocidas (`/concejalias`, `/corporacion`, etc.).
- **Configuración:** Ver `config/alternative_routes.json`.

## 📊 Metadatos Maestros

- **Dominios:** El archivo `config/domains.json` contiene la lista oficial de URLs base de los municipios canarios.
- **Casos Especiales:** `config/special_cases.json` mapea municipios específicos con sus necesidades técnicas detectadas.

## ⚠️ Lecciones Aprendidas

- **Tor Proxy:** Se implementó inicialmente soporte para Tor, pero el uso de 1 solo worker es vital para evitar bloqueos por colisión de circuitos.
- **Detección AI:** Los modelos gratuitos de OpenRouter son suficientes para extracción estructurada si el HTML está bien preprocesado.
