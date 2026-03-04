"""
Scraper especializado en sitios web estáticos mediante navegación HTTP tradicional.
INTEGRACIÓN: html2text para preservar enlaces, FILTROS para equipo de gobierno y EXPANSIÓN de mailto.
"""

import requests
import html2text
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from typing import List, Dict, Any, Set

from scrapers.base import BaseScraper
from core.logger import get_logger
from core.retry_handler import retry_with_fallback
from config import load_alternative_routes

logger = get_logger(__name__)

class HTTPScraper(BaseScraper):
    """Implementa la estrategia de scraping mediante requests y BeautifulSoup + html2text."""

    def __init__(self):
        super().__init__()
        self.alternative_routes = load_alternative_routes()
        self.max_pages = 8
        
        # KEYWORDS PRIORITARIAS (Lo que Enrique pidió localizar)
        self.priority_keywords = [
            "equipo de gobierno", "grupo de gobierno", "composición del gobierno",
            "concejales de gobierno", "gobierno municipal"
        ]
        
        # KEYWORDS GENERALES
        self.target_keywords = [
            "corporación", "concejales", "pleno", "organización política", 
            "ayuntamiento", "alcalde", "composición", "concejalias", 
            "organigrama", "estructura", "directorio"
        ]

        # LISTA NEGRA (Para no gastar tokens en años antiguos o noticias)
        self.blacklist = [
            '2011', '2015', '2019', '2022', 
            '/noticias/', '/actualidad/', '/hemeroteca/', '/historico/'
        ]

    def can_handle(self, municipality: Dict[str, Any]) -> bool:
        return True

    def scrape(self, municipality_info: Dict[str, Any]) -> Dict[str, Any]:
        """Ejecuta el rastreo y extracción HTTP."""
        muni_name = municipality_info['municipality']
        base_url = municipality_info['url']
        
        if not base_url.startswith('http'):
            base_url = 'https://' + base_url
            
        logger.info(f"[{muni_name}] Iniciando scraping HTTP en {base_url}")
        
        urls_to_visit = [base_url]
        
        domain = urlparse(base_url).netloc
        if domain in self.alternative_routes:
            for route in self.alternative_routes[domain]:
                alt_url = urljoin(base_url, route)
                if alt_url not in urls_to_visit:
                    urls_to_visit.insert(0, alt_url)

        processed_urls: Set[str] = set()
        master_data: List[Dict] = []

        while urls_to_visit and len(processed_urls) < self.max_pages:
            current_url = urls_to_visit.pop(0)
            if current_url in processed_urls:
                continue
            
            # Filtro de seguridad: No entrar en URLs de la lista negra
            if any(forbidden in current_url.lower() for forbidden in self.blacklist):
                logger.debug(f"[{muni_name}] Ignorando URL por lista negra: {current_url}")
                continue

            try:
                # GESTIÓN DE PROXY (TOR):
                # Por defecto, el sistema usa las variables de entorno HTTP_PROXY y HTTPS_PROXY.
                # Si el municipio requiere conexión directa (use_proxy=False), anulamos los proxies.
                proxies = None
                if not use_proxy:
                    # Inyectamos diccionarios vacíos para forzar a la librería requests
                    # a ignorar las variables de entorno del sistema.
                    proxies = {"http": None, "https": None}
                    
                html = self._fetch_url(current_url, proxies=proxies)
                if not html:
                    continue
                
                processed_urls.add(current_url)
                soup = BeautifulSoup(html, 'html.parser')
                
                # Usamos html2text y expandimos mailto para que la IA vea todo claro
                text_content = self._get_clean_text(soup, base_url)
                
                logger.info(f"[{muni_name}] Consultando IA para {current_url}...")
                raw_data = self.extractor.extract(text_content)
                
                if raw_data:
                    cleaned_data = self.validator.process_data_list(raw_data)
                    for item in cleaned_data:
                        item['source_url'] = current_url
                        if item not in master_data:
                            master_data.append(item)

                # Buscar más enlaces relevantes
                if len(processed_urls) < self.max_pages:
                    new_links = self._find_relevant_links(soup, base_url, processed_urls)
                    # Insertar al principio para priorizar los mejores links encontrados
                    for link in reversed(new_links):
                        if link not in urls_to_visit:
                            urls_to_visit.insert(0, link)

            except Exception as e:
                logger.error(f"[{muni_name}] Error procesando {current_url}: {e}")

        status = "success" if master_data else "error"
        return self._create_result(
            municipality=muni_name,
            url=base_url,
            status=status,
            data=master_data,
            error=None if master_data else "No se encontró información relevante",
            method="HTTP"
        )

    @retry_with_fallback(max_retries=3, backoff=2)
    def _fetch_url(self, url: str, proxies: Dict[str, str] = None) -> str:
        """
        Realiza la petición HTTP real.
        El parámetro 'proxies' decide si se usa la red Tor o conexión directa.
        """
        # verify=False se usa porque muchos ayuntamientos tienen certificados SSL mal configurados.
        response = requests.get(url, timeout=30, verify=False, proxies=proxies)
        response.raise_for_status()
        response.encoding = response.apparent_encoding
        return response.text

    def _get_clean_text(self, soup: BeautifulSoup, base_url: str = "") -> str:
        """
        Limpia el HTML, expande enlaces mailto ocultos y convierte a Markdown.
        """
        # 1. TRUCO DE ORO: Exponer emails ocultos en mailto:
        # Esto transforma <a href="mailto:x@y.com">Email</a> en "Email [EMAIL_DETECTADO: x@y.com]"
        for a in soup.find_all('a', href=True):
            href = a['href']
            if 'mailto:' in href:
                # Extraer el email limpio (sin ?subject=...)
                try:
                    email = href.replace('mailto:', '').split('?')[0].strip()
                    if email:
                        # Modificamos el texto del enlace en memoria para que html2text lo capture
                        current_text = a.get_text(strip=True)
                        a.string = f"{current_text} [EMAIL_DETECTADO: {email}]"
                except Exception:
                    pass

        # 2. Limpieza preliminar de ruido (Scripts, estilos, etc)
        for tag in soup(['script', 'style', 'noscript', 'iframe', 'svg', 'footer', 'nav', 'header']):
            tag.decompose()

        # 3. Configurar html2text
        h = html2text.HTML2Text()
        h.ignore_links = False
        h.ignore_images = True
        h.body_width = 0
        h.protect_links = True
        
        if base_url:
            h.baseurl = base_url

        try:
            return h.handle(str(soup))
        except Exception:
            return soup.get_text(separator='\n', strip=True)

    def _find_relevant_links(self, soup: BeautifulSoup, base_url: str, processed: Set[str]) -> List[str]:
        """Busca enlaces prioritarios y generales, filtrando el pasado."""
        priority_found = []
        general_found = []
        
        for a in soup.find_all('a', href=True):
            href = a['href']
            full_url = urljoin(base_url, href)
            
            # Solo navegación interna y no procesada
            if urlparse(full_url).netloc != urlparse(base_url).netloc or full_url in processed:
                continue
            
            # FILTRO: Si el link contiene años viejos, ignorar
            if any(forbidden in full_url.lower() for forbidden in self.blacklist):
                continue
                
            link_text = a.get_text().lower()
            
            # PRIORIDAD: Equipo/Grupo de Gobierno
            if any(kw in link_text for kw in self.priority_keywords):
                priority_found.append(full_url)
            # GENERAL: Otras keywords
            elif any(kw in link_text for kw in self.target_keywords):
                general_found.append(full_url)
        
        # Devolvemos primero los de prioridad
        return list(set(priority_found)) + list(set(general_found))