"""
Punto de entrada principal para el Scraper de Políticos de Canarias.
"""

import json
import os
import time
from pathlib import Path
from dotenv import load_dotenv

from core.logger import get_logger
from core.strategy_manager import StrategyManager
from config import load_domains, load_special_cases

# Cargar variables de entorno
load_dotenv()

logger = get_logger("ScrapPoliticos")

class ScraperApp:
    def __init__(self):
        self.manager = StrategyManager()
        self.special_cases = load_special_cases()
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

        logger.info(f"🚀 Iniciando scraping secuencial para {len(municipalities)} municipios...")
        
        results = []
        
        for muni in municipalities:
            try:
                # Inyectar configuración especial si existe
                muni_name = muni['municipality']
                if muni_name in self.special_cases:
                    muni['config'] = self.special_cases[muni_name]

                result = self.manager.execute_pipeline(muni)
                results.append(result)
                
                # Guardado incremental por seguridad
                self._save_results(results)
                
            except Exception as e:
                logger.error(f"Error crítico procesando {muni.get('municipality')}: {e}", exc_info=True)
                
        logger.info("✅ Proceso de scraping finalizado exitosamente.")

    def _save_results(self, results):
        """Guarda los resultados en formato JSON."""
        with open(self.results_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=4, ensure_ascii=False)

if __name__ == "__main__":
    app = ScraperApp()
    app.run()
