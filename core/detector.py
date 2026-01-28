"""
Módulo para detectar automáticamente la mejor estrategia de scraping.
"""

from typing import Dict, Any
from core.logger import get_logger
from config import load_special_cases

logger = get_logger(__name__)

class StrategyDetector:
    """Decide qué estrategia de scraping es la más adecuada para un municipio."""

    def __init__(self):
        self.special_cases = load_special_cases()

    def get_best_strategy(self, municipality: Dict[str, Any]) -> str:
        """
        Retorna el nombre de la estrategia recomendada ('http', 'javascript', 'ocr').
        Actualmente prioriza la configuración manual en special_cases.json.
        """
        muni_name = municipality['municipality']
        
        # 1. Verificar configuración manual (Prioridad alta)
        if muni_name in self.special_cases:
            method = self.special_cases[muni_name].get('method')
            if method:
                logger.info(f"[{muni_name}] Estrategia manual detectada en config: {method}")
                return method.lower()

        # 2. Heurísticas automáticas (TODO: Implementar más profundidad)
        # Por ahora, si no hay caso especial, usamos HTTP estándar.
        return "http"
