"""
Módulo de extracción de datos usando IA con soporte para múltiples modelos y fallbacks.
"""

import os
import json
from typing import List, Dict, Any, Optional
import openai
from core.logger import get_logger
from core.retry_handler import retry_with_fallback
from config import load_models_config

logger = get_logger(__name__)

class AIExtractor:
    """Clase encargada de la extracción de datos estructurados mediante LLMs."""

    def __init__(self):
        self.api_key = os.getenv('OPENROUTER_API_KEY')
        self.base_url = "https://openrouter.ai/api/v1"
        self.models = load_models_config()
        
        if not self.api_key:
            logger.error("No se encontró la API KEY de OpenRouter en el entorno.")

    def extract(self, text: str) -> List[Dict[str, Any]]:
        """
        Intenta extraer datos de concejales del texto proporcionado usando IA.
        Prueba diferentes modelos secuencialmente en caso de fallos de cuota o rate limit.
        """
        if not self.api_key:
            return []

        # Limitar longitud de texto para control de tokens
        truncated_text = text[:10000]
        
        for model_id in self.models:
            try:
                logger.info(f"Intentando extracción con modelo: {model_id}")
                result = self._call_ai(truncated_text, model_id)
                if result:
                    logger.info(f"✅ Extracción exitosa con {model_id}")
                    return result
            except Exception as e:
                logger.warning(f"Error con modelo {model_id}: {e}")
                continue
        
        logger.error("Todos los modelos de IA fallaron para procesar el texto.")
        return []

    @retry_with_fallback(max_retries=2, backoff=2)
    def _call_ai(self, text: str, model_id: str) -> Optional[List[Dict[str, Any]]]:
        """Realiza la llamada efectiva a la API de OpenRouter."""
        client = openai.OpenAI(
            base_url=self.base_url,
            api_key=self.api_key
        )
        
        # 1. Extracción PREVIA de emails usando Regex (Fallback seguro)
        found_emails = self._extract_emails_regex(text)
        emails_context = ", ".join(found_emails) if found_emails else "Ninguno detectado por regex"

        prompt = f"""
        Eres un experto en scraping de datos gubernamentales.
        Tu ÚNICO objetivo es extraer la lista de CARGOS POLÍTICOS ELECTOS (Alcalde/sa y Concejales/as) del siguiente texto.
        
        CONTEXTO DE PROTECCIÓN:
        Hemos pre-detectado estos emails ocultos en el código: [{emails_context}]
        Usa esta lista para ASOCIARLOS a los políticos correspondientes si la inferencia directa falla.
        
        REGLAS ESTRICTAS DE FILTRADO:
        1. SOLO extraer personas con cargos de "Alcalde", "Alcaldesa", "Concejal", "Concejala", "Teniente de Alcalde".
        2. IGNORAR COMPLETAMENTE: Personal técnico, administrativos, secretarios, tesoreros, policía local, bedeles, o directores de área no electos.
        3. IGNORAR departamentos genéricos o emails de "información" o "registro" si no están asociados directamente a un político.

        Para cada cargo político encontrado, extrae:
        - "nombre": Nombre completo de la persona.
        - "partido": Partido político (siglas o nombre).
        - "cargo": El cargo oficial (ej: "Concejal de Urbanismo").
        - "email": Email personal o del área que dirige. (Prioriza los que coincidan con la lista pre-detectada).

        Si no encuentras cargos políticos, devuelve una lista vacía [].
        Devuelve ÚNICAMENTE un JSON válido con una lista de objetos bajo la clave "data".
        
        Texto:
        {text}
        """

        response = client.chat.completions.create(
            model=model_id,
            messages=[{"role": "user", "content": prompt}]
        )
        
        # Validación segura de la respuesta
        if not response or not response.choices:
            logger.error(f"Respuesta vacía o inválida del proveedor {model_id}")
            return None
            
        # Limpiar bloques de código markdown si existen
        content = response.choices[0].message.content
        if not content:
             return None
             
        content = content.strip()
        if content.startswith("```"):
            # Eliminar primera línea (```json) y última línea (```)
            lines = content.split('\n')
            if len(lines) >= 3:
                content = '\n'.join(lines[1:-1])
        
        try:
            data = json.loads(content)
        except json.JSONDecodeError as e:
            logger.warning(f"Error parseando JSON de {model_id}: {e}")
            logger.debug(f"Contenido no válido: {content[:100]}...")
            return None
        
        if "data" in data and isinstance(data["data"], list):
            return data["data"]
        
        return None

    def _extract_emails_regex(self, text: str) -> List[str]:
        """Extrae todos los emails únicos del texto usando regex."""
        import re
        # Regex básico pero robusto para emails
        email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
        emails = set(re.findall(email_pattern, text))
        
        # Filtrar extensiones de imagen falsas (a veces png@... pasa)
        valid_emails = [e for e in emails if not e.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.css', '.js'))]
        
        return list(valid_emails)
