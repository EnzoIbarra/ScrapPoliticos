"""
Gestor de estrategias de scraping con lógica secuencial (Waterfall).
"""

from typing import Dict, Any, List, Optional
from core.logger import get_logger
from scrapers.http_scraper import HTTPScraper
from scrapers.javascript_scraper import JavaScriptScraper

logger = get_logger(__name__)

class StrategyManager:
    """
    Orquesta la ejecución secuencial de estrategias de scraping.
    Sigue el patrón 'Waterfall':
    1. Tor + HTTP (Privacidad)
    2. Direct IP + HTTP (Velocidad/Fallback)
    3. Direct IP + JavaScript (Potencia/Fallback Final)
    """

    def __init__(self):
        self.http_scraper = HTTPScraper()
        self.js_scraper = JavaScriptScraper()

    def execute_pipeline(self, municipality: Dict[str, Any]) -> Dict[str, Any]:
        """
        Ejecuta la tubería de estrategias hasta obtener éxito.
        """
        muni_name = municipality['municipality']
        
        # 1. Nivel 1: Tor + HTTP
        logger.info(f"[{muni_name}] 🛡️ Intentando Nivel 1: HTTP + Tor (Privacidad)...")
        result = self._try_strategy(self.http_scraper, municipality, use_proxy=True)
        if self._is_success(result):
            return result
        
        # 2. Nivel 2: Direct IP + HTTP
        logger.warning(f"[{muni_name}] ⚠️ Nivel 1 falló. 🚀 Intentando Nivel 2: HTTP + IP Directa...")
        result = self._try_strategy(self.http_scraper, municipality, use_proxy=False)
        if self._is_success(result):
            return result

        # 3. Nivel 3: JavaScript (Directo)
        logger.warning(f"[{muni_name}] ⚠️ Nivel 2 falló. ☢️ Intentando Nivel 3: JavaScript + IP Directa...")
        result = self._try_strategy(self.js_scraper, municipality, use_proxy=False)
        if self._is_success(result):
            return result

        # Si todo falla
        logger.error(f"[{muni_name}] ❌ Todas las estrategias fallaron.")
        return result or self._create_failure(municipality)

    def _try_strategy(self, scraper, municipality: Dict, use_proxy: bool) -> Dict:
        """Helper para ejecutar una estrategia con configuración específica."""
        # Clonar para no mutar el original
        muni_config = municipality.copy()
        
        # Inyectar configuración
        current_config = muni_config.get('config', {})
        current_config['use_proxy'] = use_proxy
        muni_config['config'] = current_config

        try:
            return scraper.scrape(muni_config)
        except Exception as e:
            logger.error(f"Error interno en estrategia: {e}")
            return self._create_failure(municipality, str(e))

    def _is_success(self, result: Dict) -> bool:
        """Determina si un resultado es válido y exitoso."""
        if not result:
            return False
            
        status = result.get('status')
        data = result.get('data')
        
        # Éxito si status es success Y hay datos extraídos
        # A veces success es falso positivo si la IA devuelve lista vacía
        success = status == 'success' and data and len(data) > 0
        
        if status == 'success' and not data:
            logger.warning(f"Estrategia reportó éxito pero sin datos (Posible fallo IA/Selector).")
            return False
            
        return success

    def _create_failure(self, municipality: Dict, error: str = "Todas las estrategias agotadas") -> Dict:
        return {
            "municipality": municipality['municipality'],
            "url": municipality['url'],
            "status": "error",
            "method": "AllStrategies",
            "data": [],
            "error": error
        }
