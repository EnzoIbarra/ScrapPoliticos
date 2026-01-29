import json
from pathlib import Path

def clean_data():
    """
    Limpia data/valid_results.json eliminando registros que no son políticos.
    (Elimina Organizaciones, Departamentos, etc. heredados de ejecuciones anteriores)
    """
    file_path = Path("data/valid_results.json")
    if not file_path.exists():
        print("No existe data/valid_results.json")
        return

    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    cleaned_data = []
    total_removed = 0
    
    # Palabras CLAVE que DEBEN estar (Whitelist de Cargos Políticos)
    keywords_must_have = ["alcalde", "alcaldesa", "concejal", "concejala", "teniente"]
    
    # Palabras que INVALIDAN el contacto (Blacklist de Departamentos mal clasificados)
    keywords_forbidden = [
        "concejalia", "concejalía", "departamento", "oficina", "área", "area", 
        "servicio", "secretaría", "secretaria", "tesorería", "tesoreria", 
        "ayuntamiento", "gabinete", "registro", "policía", "policia", 
        "intervención", "intervencion", "urbanismo", "corporación", "corporacion",
        "presidencia", "recaudación", "recaudacion"
    ]

    for item in data:
        muni = item.get("municipality")
        contacts = item.get("data", [])
        valid_contacts = []
        
        for person in contacts:
            # Normalizar a minúsculas para comparar
            name_lower = person.get("nombre", "").lower().strip()
            cargo_lower = person.get("cargo", "").lower().strip() if person.get("cargo") else ""
            tipo_lower = person.get("tipo", "").lower() if person.get("tipo") else ""
            
            # Combinar texto relevante para búsqueda
            full_text = f"{name_lower} {cargo_lower}"
            
            # 1. Filtro DURO de tipo si fue detectado como Organización
            if "organización" in tipo_lower or "organizacion" in tipo_lower:
                total_removed += 1
                continue

            # 2. Filtro de BLACKLIST (Si el nombre u cargo suena a departamento)
            # Ejemplo: "Concejalía de Cultura" -> Contiene "concejalía" (BAD)
            # Ejemplo: "Oficina de Alcaldía" -> Contiene "oficina" y "alcaldía" (BAD, queremos la persona)
            if any(bad in name_lower for bad in keywords_forbidden):
                # Caso borde: A veces el cargo es "Concejal de..." pero el nombre es correcto.
                # Checamos SIEMPRE el nombre. Si el NOMBRE dice "Concejalia" es un depto.
                total_removed += 1
                continue

            # 3. Filtro de WHITELIST (Debe ser un político explícito)
            # Debe tener "alcalde" o "concejal" en alguna parte del cargo o nombre
            if not any(good in full_text for good in keywords_must_have):
                 # Si no menciona alcalde/concejal, probablemente es un técnico o "Responsable de X"
                total_removed += 1
                continue
            
            # Si pasa todos los filtros, es una persona política válida
            valid_contacts.append(person)
            
        if valid_contacts:
            item["data"] = valid_contacts
            cleaned_data.append(item)
        else:
            # Si se quedó sin contactos válidos, ¿lo mandamos a retry?
            # Por ahora lo dejamos en valid pero vacio? No, mejor no guardarlo como valid si no tiene políticos.
            # Ojo: Si lo quitamos de aqui, deberia ir a retry. 
            # Para simplificar, actualizaremos el JSON con lo que quede.
            pass

    # Guardar backup por seguridad
    with open("data/valid_results_backup.json", "w", encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

    # Sobrescribir
    with open(file_path, "w", encoding='utf-8') as f:
        json.dump(cleaned_data, f, indent=4, ensure_ascii=False)
        
    print(f"🧹 Limpieza completada.")
    print(f"❌ Eliminados {total_removed} registros 'basura' (Organizaciones/Deptos).")
    print(f"✅ Municipios válidos restantes: {len(cleaned_data)}")

if __name__ == "__main__":
    clean_data()
