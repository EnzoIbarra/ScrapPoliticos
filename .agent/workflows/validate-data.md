---
description: Validación de la integridad y calidad de los datos extraídos
---

# Workflow: Validación de Datos (Docker)

Este workflow describe cómo validar los datos después de una ejecución de scraping usando Docker.

## Pasos

1. **Ejecutar script de validación:**
   // turbo

```powershell
make validate
```

O usando docker-compose directamente:
// turbo

```powershell
docker-compose run --rm scraper python tests/validate_improvements.py
```

2. **Revisar resultados de validación:**
   Verifica el archivo `data/validation_results.json` para encontrar discrepancias o errores de extracción.

3. **Verificar casos especiales:**
   Si hay problemas en municipios específicos, ejecuta el test de casos especiales:
   // turbo

```powershell
docker-compose run --rm scraper python tests/test_special_cases.py
```
