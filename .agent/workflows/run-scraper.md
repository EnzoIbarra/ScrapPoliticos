# Workflow: Ejecución del Scraper (Docker)

Este workflow describe los pasos para ejecutar el sistema de scraping completo utilizando Docker, garantizando un entorno consistente.

## Pasos

1. **Configuración:**
   Asegúrate de que el archivo `.env` contenga la clave `OPENROUTER_API_KEY`.

2. **Preparar la infraestructura:**
   // turbo

```powershell
docker-compose build
```

3. **Ejecutar el scraper:**
   // turbo

```powershell
docker-compose up scraper
```

4. **Verificar resultados:**
   Los resultados se sincronizan automáticamente en tu carpeta local:
   - Datos: `data/results.json`
   - Logs: `logs/scraper.log`
