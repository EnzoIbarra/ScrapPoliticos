"""
Script de validación para probar las mejoras del scraper
en los 4 municipios con URLs corregidas
"""

import json
import os
import sys

# Añadir el directorio raíz al path para que los imports funcionen
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scrapers.http_scraper import HTTPScraper
from config import load_domains


def validate_improvements():
    print("🚀 Iniciando validación de mejoras (URLs corregidas)...")
    
    municipalities = load_domains()
    scraper = HTTPScraper()

    print("=" * 80)
    print("VALIDACIÓN DE MEJORAS DEL SCRAPER")
    print("=" * 80)
    print(f"\nProbando {len(TEST_MUNICIPALITIES)} municipios con URLs corregidas...\n")
    
    results = []
    
    for muni in TEST_MUNICIPALITIES:
        print("\n" + "=" * 80)
        print(f"PROCESANDO: {muni['municipality']}")
        print("=" * 80)
        
        try:
            result = scrape_municipality(muni)
            results.append(result)
            
            # Mostrar resumen
            if result.get('status') == 'success':
                data_count = len(result.get('data', []))
                pages_count = len(result.get('pages_scanned', []))
                print(f"\n✅ ÉXITO: {data_count} registros encontrados en {pages_count} páginas")
                
                if data_count > 0:
                    print("\n📋 Primeros 3 registros:")
                    for i, item in enumerate(result['data'][:3], 1):
                        print(f"  {i}. {item.get('nombre', 'N/A')} - {item.get('cargo', 'N/A')}")
            else:
                print(f"\n❌ ERROR: {result.get('error', 'Unknown error')}")
                
        except Exception as e:
            print(f"\n❌ EXCEPCIÓN: {str(e)}")
            results.append({
                "municipality": muni['municipality'],
                "url": muni['url'],
                "status": "exception",
                "error": str(e)
            })
    
    # Guardar resultados
    output_path = os.path.join('data', 'validation_results.json')
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=4, ensure_ascii=False)
    
    print("\n\n" + "=" * 80)
    print("RESUMEN DE VALIDACIÓN")
    print("=" * 80)
    
    success_count = sum(1 for r in results if r.get('status') == 'success' and len(r.get('data', [])) > 0)
    total_records = sum(len(r.get('data', [])) for r in results if r.get('status') == 'success')
    
    print(f"\n✅ Municipios exitosos: {success_count}/{len(TEST_MUNICIPALITIES)}")
    print(f"📊 Total de registros extraídos: {total_records}")
    print(f"💾 Resultados guardados en: {output_path}\n")

if __name__ == "__main__":
    main()
