import re
import json
import os

def extract_domains():
    file_path = "Obtener dominios web ayuntamientos Canarias.md"
    if not os.path.exists(file_path):
        print(f"Error: {file_path} not found")
        return

    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Regex for table pattern: | **Municipio** | Dominio |
    table_pattern = re.compile(r'\|\s*\*\*([^*]+)\*\*\s*\|\s*(www\.[^\s|]+)')
    
    # Regex for list pattern (La Palma): * **Barlovento:** www.barlovento.es
    list_pattern = re.compile(r'\*\s*\*\*([^*:]+):?\*\*\s*(www\.[^\s|]+)')

    domains = []
    seen_names = set()
    
    blacklist = ["Punto de Acceso", "Municipio"]

    def add_domain(name, url):
        name = name.strip()
        url = url.strip().rstrip('.')
        if name in blacklist or name in seen_names:
            return
        if not url.startswith("www."):
            return
        domains.append({"municipality": name, "url": url})
        seen_names.add(name)

    # Extract from tables
    for match in table_pattern.finditer(content):
        add_domain(match.group(1), match.group(2))

    # Extract from lists
    for match in list_pattern.finditer(content):
        add_domain(match.group(1), match.group(2))

    print(f"Extracted {len(domains)} unique domains.")
    
    # Validation
    if len(domains) != 88:
        print("Warning: Expected 88 municipalities, found", len(domains))
        # Log missing or extra? 
        # For now let's just proceed if close or investigate if very different.

    output_path = "data/domains.json"
    os.makedirs("data", exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(domains, f, indent=4, ensure_ascii=False)
    
    print(f"Saved to {output_path}")

if __name__ == "__main__":
    extract_domains()
