"""
Gestor de estrategias de scraping con lógica secuencial (Waterfall), soporte OCR 
y enriquecimiento de datos (Deep Crawl).
"""

from typing import Dict, Any
from core.logger import get_logger
from scrapers.http_scraper import HTTPScraper
from scrapers.javascript_scraper import JavaScriptScraper
from scrapers.ocr_scraper import OCRScraper
from core.enricher import DataEnricher

logger = get_logger(__name__)

class StrategyManager:
    """
    Orquesta la ejecución secuencial de estrategias de scraping.
    """

    def __init__(self):
        self.http_scraper = HTTPScraper()
        self.js_scraper = JavaScriptScraper()
        self.ocr_scraper = OCRScraper()
        self.enricher = DataEnricher()

    def execute_pipeline(self, municipality: Dict[str, Any]) -> Dict[str, Any]:
        """
        Ejecuta la tubería de estrategias.
        """
        muni_name = municipality['municipality']
        
        # --- CORRECCIÓN CRÍTICA ---
        # Aseguramos que la URL base tenga esquema (https://) para que el Enricher no falle.
        base_url = municipality['url']
        if not base_url.startswith('http'):
            base_url = 'https://' + base_url
            
        config = municipality.get('config', {})

        # 0. CASO ESPECIAL: Forzar OCR si la configuración lo pide (ej: Puntallana)
        if config.get('requires') == 'ocr':
            logger.info(f"[{muni_name}] 📸 Detectado caso especial: Forzando OCR...")
            result = self._try_strategy(self.ocr_scraper, municipality, use_proxy=False)
            return self._enrich_result(result, base_url)

        # 0. CASO ESPECIAL: Forzar JS si la configuración lo pide (ej: Santa Cruz)
        if config.get('requires') == 'javascript':
            logger.info(f"[{muni_name}] ☢️ Detectado caso especial: Forzando JS...")
            result = self._try_strategy(self.js_scraper, municipality, use_proxy=False)
            return self._enrich_result(result, base_url)

        # 1. Nivel 1: Tor + HTTP
        logger.info(f"[{muni_name}] 🛡️ Intentando Nivel 1: HTTP + Tor (Privacidad)...")
        result = self._try_strategy(self.http_scraper, municipality, use_proxy=True)
        if self._is_success(result):
            return self._enrich_result(result, base_url)
        
        # 2. Nivel 2: Direct IP + HTTP
        logger.warning(f"[{muni_name}] ⚠️ Nivel 1 falló. 🚀 Intentando Nivel 2: HTTP + IP Directa...")
        result = self._try_strategy(self.http_scraper, municipality, use_proxy=False)
        if self._is_success(result):
            return self._enrich_result(result, base_url)

        # 3. Nivel 3: JavaScript (Directo)
        logger.warning(f"[{muni_name}] ⚠️ Nivel 2 falló. ☢️ Intentando Nivel 3: JavaScript + IP Directa...")
        result = self._try_strategy(self.js_scraper, municipality, use_proxy=False)
        if self._is_success(result):
            return self._enrich_result(result, base_url)

        # Si todo falla
        logger.error(f"[{muni_name}] ❌ Todas las estrategias fallaron.")
        return result or self._create_failure(municipality)

    def _enrich_result(self, result: Dict, base_url: str) -> Dict:
        """
        Si la extracción fue exitosa, pasa los datos por el DataEnricher
        para buscar emails en los perfiles individuales.
        """
        if result and result.get('status') == 'success' and result.get('data'):
            original_data = result['data']
            # Llamamos al enricher con la URL corregida (con https)
            enriched_data = self.enricher.enrich_emails(original_data, base_url)
            result['data'] = enriched_data
            
        return result

    def _try_strategy(self, scraper, municipality: Dict, use_proxy: bool) -> Dict:
        """Helper para ejecutar una estrategia con configuración específica."""
        muni_config = municipality.copy()
        
        # Inyectar configuración de proxy
        current_config = muni_config.get('config', {})
        if isinstance(current_config, dict):
            current_config = current_config.copy()
        else:
            current_config = {}
            
        current_config['use_proxy'] = use_proxy
        muni_config['config'] = current_config

        try:
            return scraper.scrape(muni_config)
        except Exception as e:
            logger.error(f"Error interno en estrategia: {e}")
            return self._create_failure(municipality, str(e))

    def _is_success(self, result: Dict) -> bool:
        if not result:
            return False
        status = result.get('status')
        data = result.get('data')
        # Éxito si status es success Y hay datos extraídos
        success = status == 'success' and data and len(data) > 0
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