"""
Punto de entrada principal para el Scraper de Políticos de Canarias.
"""

import json
import os
import time
from pathlib import Path
from dotenv import load_dotenv

from core.logger import get_logger
from core.detector import StrategyDetector
from config import load_domains
from scrapers.http_scraper import HTTPScraper
from scrapers.javascript_scraper import JavaScriptScraper
from scrapers.ocr_scraper import OCRScraper

# Cargar variables de entorno
load_dotenv()

logger = get_logger("ScrapPoliticos")

class ScraperApp:
    def __init__(self):
        self.detector = StrategyDetector()
        self.scrapers = {
            "http": HTTPScraper(),
            "javascript": JavaScriptScraper(),
            "playwright": JavaScriptScraper(), # Alias
            "ocr": OCRScraper()
        }
        self.output_dir = Path("data")
        self.output_dir.mkdir(exist_ok=True)
        self.results_file = self.output_dir / "results.json"

    def run(self):
        """Ejecuta el proceso completo de scraping para todos los municipios."""
        source_file = os.getenv("SOURCE_FILE")
        
        if source_file and  Path(source_file).exists():
             logger.info(f"📂 Cargando municipios desde archivo fuente: {source_file}")
             with open(source_file, 'r', encoding='utf-8') as f:
                 municipalities = json.load(f)
        else:
            municipalities = load_domains()

        logger.info(f"🚀 Iniciando scraping para {len(municipalities)} municipios...")
        
        results = []
        
        for muni in municipalities:
            try:
                result = self.process_municipality(muni)
                results.append(result)
                
                # Guardado incremental por seguridad
                self._save_results(results)
                
            except Exception as e:
                logger.error(f"Error crítico procesando {muni.get('municipality')}: {e}")
                
        logger.info("✅ Proceso de scraping finalizado exitosamente.")

    def process_municipality(self, muni: dict):
        """Orquesta la extracción para un solo municipio."""
        muni_name = muni['municipality']
        
        # Detectar mejor estrategia
        force_strategy = os.getenv("FORCE_STRATEGY")
        if force_strategy:
            strategy_name = force_strategy
            logger.info(f"[{muni_name}] Forzando estrategia: {strategy_name}")
        else:
            strategy_name = self.detector.get_best_strategy(muni)

        scraper = self.scrapers.get(strategy_name, self.scrapers["http"])
        
        # Enriquecer muni con config si es caso especial
        if muni_name in self.detector.special_cases:
            muni['config'] = self.detector.special_cases[muni_name]
        
        # Ejecutar
        logger.info(f"[{muni_name}] Usando estrategia: {strategy_name}")
        return scraper.scrape(muni)

    def _save_results(self, results):
        """Guarda los resultados en formato JSON."""
        with open(self.results_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=4, ensure_ascii=False)

if __name__ == "__main__":
    app = ScraperApp()
    app.run()
