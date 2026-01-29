- `/config`: Archivos de configuración JSON (dominios, rutas, modelos).
- `/core`: Lógica central (IA, validación, reintentos).
- `/scrapers`: Diferentes motores de scraping.
- `/docs`: Documentación técnica detallada.
- `/tests`: Scripts de validación y pruebas.
- `/scripts`: Utilidades adicionales.

## 🛡️ Robustez

- **Detección Automática**: Selecciona la mejor estrategia según el municipio.
- **Reintentos**: Sistema de reintentos con backoff exponencial.
- **Validación de Datos**: Limpieza automática de nombres, emails y cargos.

## 📜 Reglas de Desarrollo

Consulta [GEMINI.md](GEMINI.md) para conocer los estándares de código, arquitectura y commits seguidos en este proyecto.

---

**Versión**: 2.0.0 | **Arquitectura**: Vertical Slice
