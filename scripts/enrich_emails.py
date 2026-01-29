import json
import os
import sys
from pathlib import Path

# Agregar directorio raíz al path para importar 'core'
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.strategy_manager import StrategyManager
from core.logger import get_logger

# Configurar logger simple
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("Enricher")

def enrich_emails():
    """
    Recorre los municipios en valid_results.json y re-escanea
    para intentar recuperar emails usando la nueva lógica de extracción.
    """
    input_file = Path("data/valid_results.json")
    if not input_file.exists():
        logger.error("No existe valid_results.json")
        return

    with open(input_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    manager = StrategyManager()
    enriched_count = 0
    
    total = len(data)
    logger.info(f"Iniciando enriquecimiento de {total} municipios...")

    for i, item in enumerate(data):
        muni = item.get("municipality")
        url = item.get("url")
        contacts = item.get("data", [])

        # Chequear si faltan emails (si ya todos tienen, saltamos)
        all_have_email = all(c.get("email") for c in contacts if c.get("cargo"))
        if all_have_email and contacts:
            logger.info(f"[{i+1}/{total}] {muni}: Skipping (Completo)")
            continue

        logger.info(f"[{i+1}/{total}] {muni}: Re-escaneando para buscar emails...")
        
        # FAST-TRACK: Intentar Directo (Level 2) -> JS (Level 3). Ignorando Tor (Level 1).
        result = None
        
        # 1. Level 2: Direct HTTP
        logger.info(f"[{muni}] 🚀 [FAST-TRACK] Intentando HTTP Directo...")
        http_result = manager.http_scraper.scrape({
            "municipality": muni, 
            "url": url, 
            "config": {"use_proxy": False}
        })
        
        if http_result and http_result["status"] == "success" and http_result.get("data"):
            result = http_result
            logger.info(f"[{muni}] ✅ Éxito con HTTP Directo.")
        else:
            # 2. Level 3: JS Direct
            logger.info(f"[{muni}] ☢️ [FAST-TRACK] Intentando JS Directo...")
            js_result = manager.js_scraper.scrape({
                "municipality": muni, 
                "url": url, 
                "config": {"use_proxy": False}
            })
            if js_result and js_result["status"] == "success":
                result = js_result
                logger.info(f"[{muni}] ✅ Éxito con JS Directo.")
            else:
                 logger.info(f"[{muni}] ❌ Fallaron ambas estrategias directas.")
                 result = None

        if result and result.get("status") == "success":
            new_contacts = result.get("data", [])
            
            # Fusionar lógica: Si encontramos nuevos contactos con email, actualizamos.
            # O mejor, reemplazamos la lista si la nueva parece mejor.
            
            # Contar emails actuales vs nuevos
            old_emails = sum(1 for c in contacts if c.get("email"))
            new_emails = sum(1 for c in new_contacts if c.get("email"))
            
            if new_emails > old_emails:
                logger.info(f"✅ {muni}: MEJORA DETECTADA! ({old_emails} -> {new_emails} emails)")
                item["data"] = new_contacts
                enriched_count += 1
            elif len(new_contacts) > len(contacts):
                 logger.info(f"✅ {muni}: Más contactos detectados ({len(contacts)} -> {len(new_contacts)})")
                 item["data"] = new_contacts
                 enriched_count += 1
            else:
                logger.info(f"⚠️ {muni}: Sin mejora significativa.")
        else:
             logger.error(f"❌ {muni}: Falló el re-escaneo.")

        # Guardar progresivamente cada 5
        if i % 5 == 0:
            with open(input_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4, ensure_ascii=False)

    # Guardado final
    with open(input_file, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

    logger.info(f"🏁 Enriquecimiento finalizado. Municipios mejorados: {enriched_count}")

if __name__ == "__main__":
    enrich_emails()
