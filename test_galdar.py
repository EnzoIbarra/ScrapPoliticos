# Archivo: test_galdar.py
import json
import logging
from core.strategy_manager import StrategyManager
from dotenv import load_dotenv


load_dotenv()

# 1. Configurar logs para ver todo el detalle
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("TestGaldar")

# 2. Datos de prueba: El caso de Gáldar que fallaba
galdar_test = {
    "municipality": "Gáldar",
    "url": "https://www.galdar.es/organigrama-municipal-2023-2027/",
    "config": {
        "use_proxy": False,  # Sin proxy para ir rápido
        "requires": None     # Dejar que el StrategyManager decida
    }
}

def run_test():
    print("\n" + "="*60)
    print("🚀 INICIANDO PRUEBA DE CONCEPTO: Deep Crawl (Enricher)")
    print("="*60 + "\n")

    # 3. Instanciar el Manager (que ya incluye tu nuevo Enricher)
    manager = StrategyManager()

    # 4. Ejecutar solo para Gáldar
    result = manager.execute_pipeline(galdar_test)

    # 5. Mostrar resultados
    print("\n" + "="*60)
    print("📊 RESULTADOS FINAL:")
    print("="*60)
    
    # Imprimimos el JSON bonito
    print(json.dumps(result, indent=2, ensure_ascii=False))

    # Validación rápida visual
    if result.get('data'):
        con_email = [p for p in result['data'] if p.get('email')]
        print(f"\n✅ Total encontrados: {len(result['data'])}")
        print(f"📧 Con Email recuperado: {len(con_email)}")
        
        if con_email:
            print(f"\nEjemplo de éxito: {con_email[0]['nombre']} -> {con_email[0]['email']}")
            print(f"Fuente del email: {con_email[0].get('email_source', 'Desconocida')}")
    else:
        print("\n❌ Algo falló. No hay datos.")

if __name__ == "__main__":
    run_test()