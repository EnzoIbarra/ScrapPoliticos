"""
Clase base para todos los scrapers.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List
from core.logger import get_logger
from core.ai_extractor import AIExtractor
from core.validator import DataValidator

logger = get_logger(__name__)

class BaseScraper(ABC):
    """Interfaz y funcionalidad base para estrategias de scraping."""

    def __init__(self):
        self.extractor = AIExtractor()
        self.validator = DataValidator()

    @abstractmethod
    def scrape(self, municipality: Dict[str, Any]) -> Dict[str, Any]:
        """Ejecuta la estrategia de scraping para el municipio dado."""
        pass

    def _create_result(self, municipality: str, url: str, status: str, data: List[Dict] = None, error: str = None, method: str = None) -> Dict[str, Any]:
        """Crea un objeto de resultado estandarizado."""
        return {
            "municipality": municipality,
            "url": url,
            "status": status,
            "method": method or self.__class__.__name__,
            "data": data or [],
            "error": error
        }
