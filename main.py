"""
Punto de entrada principal para el Scraper de Políticos de Canarias.
Genera JSON y CSV simultáneamente.
"""

import json
import os
import pandas as pd 
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
        
        # Configuración de carpetas
        self.output_dir = Path("data")
        self.output_dir.mkdir(exist_ok=True)
        
        # Archivos de salida
        self.results_json = self.output_dir / "results.json"
        self.results_csv = self.output_dir / "resultados_consolidados.csv"

    def run(self):
        """Ejecuta el proceso completo de scraping para todos los municipios."""
        source_file = os.getenv("SOURCE_FILE")
        
        if source_file and Path(source_file).exists():
             logger.info(f"📂 Cargando municipios desde archivo fuente: {source_file}")
             with open(source_file, 'r', encoding='utf-8') as f:
                 municipalities = json.load(f)
        else:
            municipalities = load_domains()

        logger.info(f"🚀 Iniciando scraping secuencial para {len(municipalities)} municipios...")
        
        results = []
        
        for i, muni in enumerate(municipalities):
            try:
                muni_name = muni['municipality']
                logger.info(f"👉 Procesando {i+1}/{len(municipalities)}: {muni_name}")

                # Inyectar configuración especial si existe
                if muni_name in self.special_cases:
                    muni['config'] = self.special_cases[muni_name]

                # Ejecutar Pipeline
                result = self.manager.execute_pipeline(muni)
                results.append(result)
                
                # --- GUARDADO INCREMENTAL (JSON y CSV) ---
                # Esto es clave: guarda cada vez que termina un municipio.
                # Si falla en el 80, no pierdes los 79 anteriores.
                self._save_json(results)
                self._save_csv_incremental(results)
                
            except Exception as e:
                logger.error(f"Error crítico procesando {muni.get('municipality')}: {e}", exc_info=True)
                
        logger.info(f"✅ FINALIZADO. Archivos guardados en carpeta 'data/':")
        logger.info(f"   📄 JSON: {self.results_json}")
        logger.info(f"   📊 CSV:  {self.results_csv}")

    def _save_json(self, results):
        """Guarda los resultados en formato JSON."""
        with open(self.results_json, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=4, ensure_ascii=False)

    def _save_csv_incremental(self, results):
        """Convierte los resultados acumulados a CSV."""
        all_rows = []
        
        for record in results:
            muni_name = record.get('municipality', 'Desconocido')
            status = record.get('status', 'error')
            url_origen = record.get('url', '')
            
            # Si hay datos (personas encontradas)
            if record.get('data'):
                for persona in record['data']:
                    # Aplanamos el diccionario para el CSV
                    row = {
                        'Municipio': muni_name,
                        'Estado Scraping': status,
                        'Nombre': persona.get('nombre'),
                        'Cargo': persona.get('cargo'),
                        'Partido': persona.get('partido'),
                        'Email': persona.get('email'), # <--- EL DATO IMPORTANTE
                        'URL Perfil': persona.get('url_perfil'),
                        'URL Origen': url_origen
                    }
                    all_rows.append(row)
            else:
                # Si no hubo datos, guardamos una fila vacía para que conste el error
                row = {
                    'Municipio': muni_name,
                    'Estado Scraping': status,
                    'Nombre': 'SIN DATOS',
                    'Cargo': record.get('error', 'Error desconocido'),
                    'Partido': '',
                    'Email': '',
                    'URL Perfil': '',
                    'URL Origen': url_origen
                }
                all_rows.append(row)

        # Crear DataFrame y guardar
        if all_rows:
            df = pd.DataFrame(all_rows)
            # Guardamos con punto y coma (;) para que Excel lo abra fácil en español
            df.to_csv(self.results_csv, index=False, encoding='utf-8-sig', sep=';')

if __name__ == "__main__":
    app = ScraperApp()
    app.run()