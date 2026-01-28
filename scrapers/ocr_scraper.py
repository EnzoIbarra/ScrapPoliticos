"""
Scraper especializado en extraer texto de imágenes mediante OCR (Tesseract).
"""

import pytesseract
from PIL import Image
import requests
from io import BytesIO
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from typing import Dict, Any, List

from scrapers.base import BaseScraper
from core.logger import get_logger

logger = get_logger(__name__)

class OCRScraper(BaseScraper):
    """Estrategia de scraping para sitios con información incrustada en imágenes."""

    def __init__(self):
        super().__init__()
        # Configuración opcional de Tesseract si no está en el PATH
        # tesseract_path = os.getenv('TESSERACT_PATH')
        # if tesseract_path:
        #     pytesseract.pytesseract.tesseract_cmd = tesseract_path

    def can_handle(self, municipality: Dict[str, Any]) -> bool:
        """Activado por configuración de casos especiales."""
        return True

    def scrape(self, municipality_info: Dict[str, Any]) -> Dict[str, Any]:
        """Descarga imágenes, aplica OCR y envía el texto resultante a la IA."""
        muni_name = municipality_info['municipality']
        config = municipality_info.get('config', {})
        urls_to_check = config.get('urls', [])
        
        logger.info(f"[{muni_name}] Iniciando proceso OCR en {len(urls_to_check)} URLs")
        
        full_ocr_text = ""
        images_processed = 0

        for url in urls_to_check:
            try:
                response = requests.get(url, timeout=30, verify=False)
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Buscar imágenes según selectores configurados o por defecto
                selectors = config.get('image_selectors', ['img'])
                image_elements = []
                for sel in selectors:
                    image_elements.extend(soup.select(sel))
                
                for img_el in image_elements:
                    img_url = img_el.get('src')
                    if not img_url:
                        continue
                    
                    full_img_url = urljoin(url, img_url)
                    text = self._process_image_url(full_img_url, muni_name)
                    if text:
                        full_ocr_text += f"\n--- Contenido de Imagen ({full_img_url}) ---\n{text}\n"
                        images_processed += 1

            except Exception as e:
                logger.error(f"[{muni_name}] Error procesando URL {url} para OCR: {e}")

        if not full_ocr_text:
            return self._create_result(muni_name, str(urls_to_check), "error", error="No se extrajo texto de ninguna imagen", method="OCR")

        logger.info(f"[{muni_name}] OCR completado ({images_processed} imágenes). Consultando IA...")
        raw_data = self.extractor.extract(full_ocr_text)
        
        if raw_data:
            cleaned_data = self.validator.process_data_list(raw_data)
            return self._create_result(
                municipality=muni_name,
                url=str(urls_to_check),
                status="success",
                data=cleaned_data,
                method="OCR"
            )
        
        return self._create_result(muni_name, str(urls_to_check), "error", error="AI no pudo extraer datos del texto OCR", method="OCR")

    def _process_image_url(self, url: str, muni_name: str) -> str:
        """Descarga y aplica OCR a una imagen individual."""
        try:
            resp = requests.get(url, timeout=20)
            img = Image.open(BytesIO(resp.content))
            
            # Preprocesamiento básico
            # Convertir a escala de grises para mejorar OCR si es necesario
            # img = img.convert('L')
            
            text = pytesseract.image_to_string(img, lang='spa')
            return text.strip()
        except Exception as e:
            logger.debug(f"[{muni_name}] No se pudo procesar imagen {url}: {e}")
            return ""
