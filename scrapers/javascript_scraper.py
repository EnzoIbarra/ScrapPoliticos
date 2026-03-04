"""
Scraper avanzado mediante Playwright para gestionar renderizado de JavaScript y scroll automático.
"""

from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
from typing import Dict, Any, List
import time

from scrapers.base import BaseScraper
from core.logger import get_logger

logger = get_logger(__name__)

class JavaScriptScraper(BaseScraper):
    """Estrategia de scraping para sitios web dinámicos."""

    def can_handle(self, municipality: Dict[str, Any]) -> bool:
        """Se activa si el municipio está configurado explícitamente para JS."""
        # Se asume que el dispatcher superior maneja esta lógica,
        # pero aquí podría haber heurísticas de detección automática.
        return True

    def scrape(self, municipality_info: Dict[str, Any]) -> Dict[str, Any]:
        """Ejecuta Playwright para obtener el HTML renderizado."""
        muni_name = municipality_info['municipality']
        url = municipality_info['url']
        if not url.startswith('http'):
            url = f'https://{url}'
        config = municipality_info.get('config', {})
        
        logger.info(f"[{muni_name}] Iniciando Playwright para {url}")
        
        # Configuración de proxy
        use_proxy = config.get('use_proxy', True)
        launch_args = {"headless": True}
        
        if not use_proxy:
            # MANIOBRA DE CONEXIÓN DIRECTA (PLAYWRIGHT bypass):
            # Playwright lee automáticamente las variables de entorno HTTP_PROXY del sistema.
            # Para forzar una conexión directa sin pasar por Tor, debemos crear una copia 
            # del entorno de ejecución y eliminar explícitamente estas variables antes de lanzar el navegador.
            import os
            env = os.environ.copy()
            env.pop("HTTP_PROXY", None)
            env.pop("HTTPS_PROXY", None)
            launch_args["env"] = env
            logger.info(f"[{muni_name}] Desactivando proxy para Playwright (Conexión Directa)")
        
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(**launch_args)
                # Crear contexto ignorando errores HTTPS
                context = browser.new_context(ignore_https_errors=True)
                page = context.new_page()
                page.goto(url, wait_until="networkidle", timeout=300000)
                
                # Gestión de Scroll automático si se requiere
                if config.get('scroll', False):
                    self._auto_scroll(page)
                
                # Esperar selector específico si está configurado
                wait_selector = config.get('wait_selector')
                if wait_selector:
                    page.wait_for_selector(wait_selector, timeout=10000)
                
                html = page.content()
                browser.close()

            # Procesamiento post-renderizado
            soup = BeautifulSoup(html, 'html.parser')
            text_content = self._get_clean_text(soup)
            
            logger.info(f"[{muni_name}] Consultando IA con HTML renderizado...")
            raw_data = self.extractor.extract(text_content)
            
            if raw_data:
                cleaned_data = self.validator.process_data_list(raw_data)
                for item in cleaned_data:
                    item['source_url'] = url
                
                return self._create_result(
                    municipality=muni_name,
                    url=url,
                    status="success",
                    data=cleaned_data,
                    method="Playwright"
                )
            
            return self._create_result(muni_name, url, "error", error="No se extrajeron datos de IA", method="Playwright")

        except Exception as e:
            logger.error(f"[{muni_name}] Error en Playwright: {e}")
            return self._create_result(muni_name, url, "error", error=str(e), method="Playwright")

    def _auto_scroll(self, page):
        """Realiza scroll automático para cargar contenido lazy-load."""
        page.evaluate("""
            async () => {
                await new Promise((resolve) => {
                    let totalHeight = 0;
                    let distance = 100;
                    let timer = setInterval(() => {
                        let scrollHeight = document.body.scrollHeight;
                        window.scrollBy(0, distance);
                        totalHeight += distance;
                        if(totalHeight >= scrollHeight){
                            clearInterval(timer);
                            resolve();
                        }
                    }, 100);
                });
            }
        """)
        time.sleep(2)

    def _get_clean_text(self, soup: BeautifulSoup) -> str:
        """Extrae el texto relevante preservando emails ocultos en atributos."""
        # 1. Expandir mailto links para que la AI los vea
        for a in soup.find_all('a', href=True):
            href = a['href']
            if 'mailto:' in href:
                email = href.replace('mailto:', '').split('?')[0].strip()
                if email:
                    current_text = a.get_text(strip=True)
                    a.string = f"{current_text} [EMAIL: {email}]"

        # 2. Eliminar ruido
        for tag in soup(['script', 'style', 'header', 'footer', 'nav', 'aside']):
            tag.decompose()
        return soup.get_text(separator='\n', strip=True)
