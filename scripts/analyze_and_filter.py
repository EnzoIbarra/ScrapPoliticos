import json
import os
from pathlib import Path

def analyze_and_filter():
    """
    Analiza data/results.json y separa los resultados en:
    1. data/valid_results.json: Resultados con datos útiles.
    2. data/retry_queue.json: Municipios que fallaron o no trajeron datos.
    """
    base_dir = Path("data")
    results_file = base_dir / "results.json"
    valid_file = base_dir / "valid_results.json"
    retry_file = base_dir / "retry_queue.json"

    if not results_file.exists():
        print(f"❌ No se encontró {results_file}")
        return

    try:
        with open(results_file, 'r', encoding='utf-8') as f:
            results = json.load(f)
    except json.JSONDecodeError:
        print(f"❌ Error al leer {results_file}. Formato inválido.")
        return

    valid_results = []
    retry_queue = []
    
    # Cargar resultados válidos existentes para no perder datos previos
    if valid_file.exists():
        try:
            with open(valid_file, 'r', encoding='utf-8') as f:
                existing_valid = json.load(f)
                # Crear diccionario para evitar duplicados (clave: municipio)
                valid_map = {item['municipality']: item for item in existing_valid}
                print(f"♻️ Cargados {len(existing_valid)} resultados válidos previos.")
        except Exception:
            valid_map = {}
    else:
        valid_map = {}

    print(f"📊 Analizando {len(results)} registros...")

    for item in results:
        muni_name = item.get("municipality")
        status = item.get("status")
        data = item.get("data", [])
        
        # Criterio de éxito: Status success Y data no vacía
        if status == "success" and data and len(data) > 0:
            # Upsert en el mapa de válidos
            valid_map[muni_name] = item
        else:
            # Si fallo, verificar si YA teníamos un resultado válido previo
            if muni_name in valid_map:
                print(f"ℹ️ Conservando resultado válido previo para {muni_name} a pesar del fallo actual.")
                continue

            # Preparamos el item para la cola de reintento
            retry_item = {
                "municipality": muni_name,
                "url": item.get("url")
            }
            if "config" in item:
                retry_item["config"] = item["config"]
            
            retry_queue.append(retry_item)

    # Convertir mapa a lista
    valid_results = list(valid_map.values())

    # Guardar resultados válidos
    with open(valid_file, 'w', encoding='utf-8') as f:
        json.dump(valid_results, f, indent=4, ensure_ascii=False)
    
    # Guardar cola de reintento
    with open(retry_file, 'w', encoding='utf-8') as f:
        json.dump(retry_queue, f, indent=4, ensure_ascii=False)

    print("\n📝 Reporte de Análisis:")
    print(f"✅ Resultados Válidos: {len(valid_results)} (Guardados en {valid_file})")
    print(f"🔄 Para Reintentar:   {len(retry_queue)} (Guardados en {retry_file})")
    
    if len(retry_queue) > 0:
        print("\n💡 Sugerencia: Ejecuta 'make retry-failed' para procesar los fallos con mayor potencia.")

if __name__ == "__main__":
    analyze_and_filter()
