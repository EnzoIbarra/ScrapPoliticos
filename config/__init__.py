"""
Carga de configuraciones centralizadas
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Any

_CONFIG_DIR = Path(__file__).parent.parent / 'config'

def load_json_config(filename: str) -> Any:
    """
    Carga un archivo JSON de configuración.
    
    Args:
        filename: Nombre del archivo (ej: 'domains.json')
    
    Returns:
        Datos del JSON
        
    Raises:
        FileNotFoundError: Si el archivo no existe
    """
    filepath = _CONFIG_DIR / filename
    
    if not filepath.exists():
        raise FileNotFoundError(f"Configuración no encontrada: {filepath}")
    
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)


def load_domains() -> List[Dict]:
    """Carga lista de dominios municipales"""
    return load_json_config('domains.json')


def load_special_cases() -> Dict:
    """Carga casos especiales (JavaScript, OCR)"""
    try:
        return load_json_config('special_cases.json')
    except FileNotFoundError:
        return {}


def load_alternative_routes() -> Dict:
    """Carga rutas alternativas por municipio"""
    try:
        return load_json_config('alternative_routes.json')
    except FileNotFoundError:
        return {}


def load_models_config() -> List[str]:
    """
    Carga lista de modelos de IA a usar.
    Actualmente usa modelos gratuitos de OpenRouter.
    """
    return [
        "google/gemini-2.0-flash-exp:free",
        "meta-llama/llama-3.3-70b-instruct:free",
    ]
