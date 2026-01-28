"""
Scraper especializado en sitios web estáticos mediante navegación HTTP tradicional.
"""

import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from typing import List, Dict, Any, Set

from scrapers.base import BaseScraper
from core.logger import get_logger
from core.retry_handler import retry_with_fallback
from config import load_alternative_routes

logger = get_logger(__name__)

class HTTPScraper(BaseScraper):
    """Implementa la estrategia de scraping mediante requests y BeautifulSoup."""

    def __init__(self):
        super().__init__()
        self.alternative_routes = load_alternative_routes()
        self.max_pages = 8
        self.target_keywords = [
            "corporación", "concejales", "gobierno municipal", "pleno", 
            "organización política", "ayuntamiento", "alcalde", "contacto", 
            "equipo de gobierno", "composición", "concejales", "concejalias", 
            "organigrama", "estructura", "gobierno", "ayuntamiento", 
            "contacto", "directorio", "telefonos", "regimen interior"
        ]

    def can_handle(self, municipality: Dict[str, Any]) -> bool:
        """Por defecto, casi todos los municipios pueden intentarse con HTTP."""
        return True

    def scrape(self, municipality_info: Dict[str, Any]) -> Dict[str, Any]:
        """Ejecuta el rastreo y extracción HTTP."""
        muni_name = municipality_info['municipality']
        base_url = municipality_info['url']
        
        # Asegurar esquema en la URL
        if not base_url.startswith('http'):
            base_url = 'https://' + base_url
            
        logger.info(f"[{muni_name}] Iniciando scraping HTTP en {base_url}")
        
        urls_to_visit = [base_url]
        
        # Inyectar rutas alternativas si existen
        domain = urlparse(base_url).netloc
        if domain in self.alternative_routes:
            for route in self.alternative_routes[domain]:
                alt_url = urljoin(base_url, route)
                if alt_url not in urls_to_visit:
                    urls_to_visit.insert(0, alt_url)
                    logger.info(f"[{muni_name}] Priorizando ruta alternativa: {alt_url}")

        processed_urls: Set[str] = set()
        master_data: List[Dict] = []

        while urls_to_visit and len(processed_urls) < self.max_pages:
            current_url = urls_to_visit.pop(0)
            if current_url in processed_urls:
                continue
            
            try:
                html = self._fetch_url(current_url)
                if not html:
                    continue
                
                processed_urls.add(current_url)
                soup = BeautifulSoup(html, 'html.parser')
                
                # Extraer texto limpio para la IA
                text_content = self._get_clean_text(soup)
                
                # Extraer datos con IA
                logger.info(f"[{muni_name}] Consultando IA para {current_url}...")
                raw_data = self.extractor.extract(text_content)
                
                if raw_data:
                    # Validar y normalizar
                    cleaned_data = self.validator.process_data_list(raw_data)
                    for item in cleaned_data:
                        item['source_url'] = current_url
                        if item not in master_data:
                            master_data.append(item)
                    
                    # Si ya tenemos datos suficientes de personas, podríamos parar, 
                    # pero seguimos rastreando para mayor cobertura según plan.

                # Buscar más enlaces relevantes
                if len(processed_urls) < self.max_pages:
                    new_links = self._find_relevant_links(soup, base_url, processed_urls)
                    urls_to_visit.extend(new_links)

            except Exception as e:
                logger.error(f"[{muni_name}] Error procesando {current_url}: {e}")

        status = "success" if master_data else "error"
        error_msg = None if master_data else "No se encontró información relevante"
        
        return self._create_result(
            municipality=muni_name,
            url=base_url,
            status=status,
            data=master_data,
            error=error_msg,
            method="HTTP"
        )

    @retry_with_fallback(max_retries=3, backoff=2)
    def _fetch_url(self, url: str) -> str:
        """Obtiene el contenido HTML de una URL."""
        response = requests.get(url, timeout=30, verify=False)
        response.raise_for_status()
        return response.text

    def _get_clean_text(self, soup: BeautifulSoup) -> str:
        """Extrae el texto relevante eliminando ruido."""
        for tag in soup(['script', 'style', 'header', 'footer', 'nav']):
            tag.decompose()
        return soup.get_text(separator='\n', strip=True)

    def _find_relevant_links(self, soup: BeautifulSoup, base_url: str, processed: Set[str]) -> List[str]:
        """Busca enlaces que contengan palabras clave objetivo."""
        found = []
        for a in soup.find_all('a', href=True):
            href = a['href']
            full_url = urljoin(base_url, href)
            
            # Solo navegación interna
            if urlparse(full_url).netloc != urlparse(base_url).netloc:
                continue
            
            if full_url in processed:
                continue
                
            link_text = a.get_text().lower()
            if any(kw in link_text for kw in self.target_keywords):
                found.append(full_url)
        
        return list(set(found))
