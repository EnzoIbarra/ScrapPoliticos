"""
Módulo de extracción de datos usando IA con soporte para múltiples modelos y fallbacks.
VERSIÓN DIAGNÓSTICO: Incluye trazas completas de error.
"""

import os
import json
import traceback  # <--- Agregado para ver el error real
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
            logger.error("❌ CRÍTICO: No se encontró la API KEY de OpenRouter en las variables de entorno.")
        else:
            masked_key = f"{self.api_key[:10]}...{self.api_key[-4:]}"
            logger.info(f"🔑 API Key cargada correctamente: {masked_key}")

    def extract(self, text: str) -> List[Dict[str, Any]]:
        """
        Intenta extraer datos de concejales del texto proporcionado usando IA.
        """
        if not self.api_key:
            logger.error("🛑 Abortando extracción: Falta API Key.")
            return []

        # Limitar longitud de texto para control de tokens
        truncated_text = text[:60000]
        
        for model_id in self.models:
            try:
                logger.info(f"🤖 Intentando extracción con modelo: {model_id}")
                result = self._call_ai(truncated_text, model_id)
                if result:
                    logger.info(f"✅ Extracción exitosa con {model_id}")
                    return result
            except Exception as e:
                # --- AQUÍ ESTÁ EL CHIVATO ---
                logger.error(f"❌ ERROR EXTREMO con modelo {model_id}")
                logger.error(f"📉 Tipo de Error: {type(e).__name__}")
                logger.error(f"📉 Mensaje: {str(e)}")
                logger.error("👇 TRAZA TÉCNICA (Muestra esto a tu soporte):")
                traceback.print_exc()
                # -----------------------------
                continue
        
        logger.error("💀 Todos los modelos de IA fallaron para procesar el texto.")
        return []

    @retry_with_fallback(max_retries=3, backoff=2)
    def _call_ai(self, text: str, model_id: str) -> Optional[List[Dict[str, Any]]]:
        """Realiza la llamada efectiva a la API de OpenRouter."""
        
        # Validar cliente antes de llamar
        if not self.api_key:
            raise ValueError("API Key es None dentro de _call_ai")

        client = openai.OpenAI(
            base_url=self.base_url,
            api_key=self.api_key
        )
        
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
        2. IGNORAR COMPLETAMENTE: Personal técnico, administrativos, secretarios...
        
        Para cada cargo político encontrado, extrae:
        - "nombre": Nombre completo de la persona.
        - "partido": Partido político (siglas o nombre).
        - "cargo": El cargo oficial (ej: "Concejal de Urbanismo").
        - "email": Email personal o del área.
        - "url_perfil": La URL relativa o absoluta (href) que lleva a su biografía o ficha personal. (EJEMPLO: "/biografia-juan-perez" o "https://dominio.com/juan").

        Si no encuentras cargos políticos, devuelve una lista vacía [].
        Devuelve ÚNICAMENTE un JSON válido con una lista de objetos bajo la clave "data".
        
        Texto:
        {text}
        """

        response = client.chat.completions.create(
            model=model_id,
            messages=[{"role": "user", "content": prompt}]
        )
        
        if not response or not response.choices:
            logger.error(f"Respuesta vacía o inválida del proveedor {model_id}")
            return None
            
        content = response.choices[0].message.content
        if not content:
             return None
             
        content = content.strip()
        if content.startswith("```"):
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
            # Una vez extraídos, los datos vuelven al Scraper que hizo la llamada
            # para ser validados y finalmente guardados en el archivo central.
            return data["data"]
        
        return None

    def _extract_emails_regex(self, text: str) -> List[str]:
        """Extrae todos los emails únicos del texto usando regex."""
        import re
        email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
        emails = set(re.findall(email_pattern, text))
        valid_emails = [e for e in emails if not e.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.css', '.js'))]
        return list(valid_emails)