"""
Script de validación para casos especiales (Playwright + OCR)
"""

import json
import os
import sys

# Añadir el directorio raíz al path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scrapers.javascript_scraper import JavaScriptScraper
from scrapers.ocr_scraper import OCRScraper
from config import load_special_cases

def test_playwright():
    """Test de Santa Cruz de la Palma con Playwright"""
    print("\n" + "="*50)
    print("TEST 1: PLAYWRIGHT - Santa Cruz de la Palma")
    print("="*50)
    
    try:
        muni_info = {"municipality": "Santa Cruz de La Palma", "url": "www.santacruzdelapalma.es"}
        special_cases = load_special_cases()
        config = special_cases.get("Santa Cruz de La Palma", {})
        muni_info['config'] = config
        
        print("\n🚀 Iniciando scraping con Playwright...")
        scraper = JavaScriptScraper()
        result = scraper.scrape(muni_info)
        
        print(f"\n✅ Status: {result['status']}")
        
        if result['status'] == 'success':
            data_count = len(result.get('data', []))
            print(f"📊 Registros encontrados: {data_count}")
            
            if data_count > 0:
                print(f"\n📋 Primeros 5 registros:")
                for i, item in enumerate(result['data'][:5], 1):
                    nombre = item.get('nombre', 'N/A')
                    cargo = item.get('cargo', 'N/A')
                    partido = item.get('partido', 'N/A')
                    print(f"  {i}. {nombre}")
                    print(f"     Cargo: {cargo}")
                    if partido != 'N/A' and partido:
                        print(f"     Partido: {partido}")
            
            # Guardar resultado
            output_path = 'data/test_playwright_result.json'
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=4, ensure_ascii=False)
            print(f"\n💾 Resultado guardado en: {output_path}")
            
            return True
        else:
            print(f"❌ Error: {result.get('error', 'Unknown')}")
            return False
            
    except ImportError as e:
        print(f"\n❌ ERROR: Playwright no instalado")
        print(f"Ejecuta:")
        print(f"  pip install playwright")
        print(f"  playwright install chromium")
        return False
    except Exception as e:
        print(f"\n❌ EXCEPCIÓN: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_ocr():
    """Test de Puntallana con OCR"""
    print("\n\n" + "=" * 80)
    print("TEST 2: OCR - Puntallana")
    print("=" * 80)
    
    try:
        muni_info = {"municipality": "Puntallana", "url": "puntallana.es"}
        special_cases = load_special_cases()
        config = special_cases.get("Puntallana", {})
        muni_info['config'] = config
        
        print("\n🔍 Iniciando scraping con OCR...")
        scraper = OCRScraper()
        result = scraper.scrape(muni_info)
        
        print(f"\n✅ Status: {result['status']}")
        
        if result['status'] == 'success':
            data_count = len(result.get('data', []))
            images_count = result.get('images_processed', 0)
            print(f"📊 Registros encontrados: {data_count}")
            print(f"🖼️  Imágenes procesadas: {images_count}")
            
            if data_count > 0:
                print(f"\n📋 Primeros 5 registros extraídos de imágenes:")
                for i, item in enumerate(result['data'][:5], 1):
                    nombre = item.get('nombre', 'N/A')
                    cargo = item.get('cargo', 'N/A')
                    email = item.get('email', 'N/A')
                    print(f"  {i}. {nombre}")
                    print(f"     Cargo: {cargo}")
                    if email != 'N/A' and email:
                        print(f"     Email: {email}")
            
            # Guardar resultado
            output_path = 'data/test_ocr_result.json'
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=4, ensure_ascii=False)
            print(f"\n💾 Resultado guardado en: {output_path}")
            
            return True
        else:
            print(f"❌ Error: {result.get('error', 'Unknown')}")
            return False
            
    except ImportError as e:
        print(f"\n❌ ERROR: OCR no instalado")
        print(f"Ejecuta:")
        print(f"  pip install pytesseract Pillow")
        print(f"  Y descarga Tesseract desde:")
        print(f"  https://github.com/UB-Mannheim/tesseract/wiki")
        return False
    except Exception as e:
        print(f"\n❌ EXCEPCIÓN: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def main():
    print("\n" + "=" * 80)
    print("VALIDACIÓN DE CASOS ESPECIALES: PLAYWRIGHT + OCR")
    print("=" * 80)
    
    results = {
        "playwright": False,
        "ocr": False
    }
    
    # Test Playwright
    results['playwright'] = test_playwright()
    
    # Test OCR  
    results['ocr'] = test_ocr()
    
    # Resumen final
    print("\n\n" + "=" * 80)
    print("RESUMEN DE VALIDACIÓN")
    print("=" * 80)
    
    print(f"\n✅ Playwright (Santa Cruz de la Palma): {'ÉXITO' if results['playwright'] else 'FALLO'}")
    print(f"✅ OCR (Puntallana): {'ÉXITO' if results['ocr'] else 'FALLO'}")
    
    success_count = sum(results.values())
    print(f"\n📊 Tests exitosos: {success_count}/2")
    
    if success_count == 2:
        print("\n🎉 ¡Todos los tests pasaron! El sistema está listo.")
    elif success_count == 1:
        print("\n⚠️  Un test falló. Revisa las dependencias e inténtalo de nuevo.")
    else:
        print("\n❌ Ambos tests fallaron. Revisa la instalación de dependencias:")
        print("   pip install -r requirements.txt")
        print("   playwright install chromium")
        print("   Descarga Tesseract: https://github.com/UB-Mannheim/tesseract/wiki")


if __name__ == "__main__":
    main()
