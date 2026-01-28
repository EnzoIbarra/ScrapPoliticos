"""
Módulo de validación y limpieza de datos extraídos.
"""

import re
from typing import List, Dict, Any, Tuple
from core.logger import get_logger

logger = get_logger(__name__)

class DataValidator:
    """Validador y normalizador de datos de políticos y contactos."""

    def __init__(self):
        self.email_pattern = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
        
    def validate_record(self, record: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        Valida un registro individual.
        Retorna (es_valido, lista_errores).
        """
        errors = []
        
        # Validación de Nombre
        nombre = record.get('nombre', '').strip()
        if not nombre or len(nombre) < 3:
            errors.append("Nombre inexistente o demasiado corto")
            
        # Validación básica de Email si existe
        email = record.get('email')
        if email:
            email = email.strip().lower()
            if not self.email_pattern.match(email):
                errors.append(f"Email con formato inválido: {email}")
                
        return len(errors) == 0, errors

    def clean_record(self, record: Dict[str, Any]) -> Dict[str, Any]:
        """Limpia y normaliza los campos de un registro."""
        cleaned = record.copy()
        
        if 'nombre' in cleaned:
            cleaned['nombre'] = self._normalize_text(cleaned['nombre'])
        
        if 'email' in cleaned:
            cleaned['email'] = cleaned['email'].strip().lower() if cleaned['email'] else None
            
        if 'partido' in cleaned and cleaned['partido']:
            cleaned['partido'] = cleaned['partido'].upper().strip()
            
        if 'cargo' in cleaned and cleaned['cargo']:
            cleaned['cargo'] = cleaned['cargo'].capitalize().strip()
            
        return cleaned

    def _normalize_text(self, text: str) -> str:
        """Normalización básica de texto (quitar espacios extra, etc)."""
        if not text:
            return ""
        # Quitar prefijos comunes si estorban (opcional)
        # return re.sub(r'^(D\.|Dña\.|D\.ª)\s+', '', text).strip()
        return text.strip()

    def process_data_list(self, data_list: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Procesa una lista completa de registros, filtrando los inválidos."""
        processed = []
        for raw_record in data_list:
            is_valid, errors = self.validate_record(raw_record)
            if is_valid:
                processed.append(self.clean_record(raw_record))
            else:
                logger.debug(f"Registro descartado por errores: {errors} -> {raw_record}")
        return processed
