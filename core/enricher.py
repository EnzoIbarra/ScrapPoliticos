import re
import time
import requests
from urllib.parse import urljoin
from typing import List, Dict, Any
from core.logger import get_logger

logger = get_logger(__name__)

class DataEnricher:
    """
    Se encarga de completar datos faltantes navegando a las URLs de detalle (Nivel 2 de Scraping).
    """

    def __init__(self):
        # Regex estándar para emails
        self.email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
        # User agent genérico para evitar bloqueos simples
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }

    def enrich_emails(self, data: List[Dict[str, Any]], base_url: str) -> List[Dict[str, Any]]:
        """
        Recorre la lista de políticos. Si falta el email y hay URL de perfil, entra y busca.
        """
        logger.info(f"🕵️‍♂️ Iniciando fase de enriquecimiento para {len(data)} registros...")
        
        enriched_count = 0

        with requests.Session() as session:
            for persona in data:
                # Criterio: No tiene email Y tiene url de perfil
                if not persona.get('email') and persona.get('url_perfil'):
                    
                    try:
                        # Construir URL absoluta (maneja casos relativos como /biografia...)
                        target_url = urljoin(base_url, persona['url_perfil'])
                        
                        logger.debug(f"🔍 Inspeccionando detalle: {persona['nombre']} -> {target_url}")
                        
                        # Hacemos la petición (con verify=False por si acaso el SSL del ayuntamiento es viejo)
                        response = session.get(target_url, headers=self.headers, timeout=10, verify=False)
                        
                        if response.status_code == 200:
                            # Buscamos emails en el HTML crudo
                            found_emails = self._find_emails_in_text(response.text)
                            
                            if found_emails:
                                # Asignamos el primero encontrado
                                persona['email'] = found_emails[0]
                                persona['email_source'] = 'detail_page_regex' # Marca de auditoría
                                enriched_count += 1
                                logger.info(f"✅ EMAIL ENCONTRADO para {persona['nombre']}: {found_emails[0]}")
                            else:
                                logger.debug(f"❌ No se hallaron emails en {target_url}")
                        else:
                            logger.warning(f"⚠️ Error {response.status_code} al acceder a {target_url}")

                        # Pausa de cortesía para no saturar al servidor del ayuntamiento
                        time.sleep(0.5)

                    except Exception as e:
                        logger.error(f"Error enriqueciendo a {persona.get('nombre')}: {str(e)}")

        logger.info(f"🏁 Enriquecimiento finalizado. Se completaron {enriched_count} emails.")
        return data

    def _find_emails_in_text(self, text: str) -> List[str]:
        """Extrae y limpia emails de un texto."""
        emails = set(re.findall(self.email_pattern, text))
        # Filtramos falsos positivos comunes (archivos de imagen, css, etc.)
        valid_emails = [
            e for e in emails 
            if not e.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.css', '.js', '.woff'))
        ]
        return list(valid_emails)