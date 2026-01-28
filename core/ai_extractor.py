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
        
        prompt = f"""
        Eres un experto en scraping y estructuración de datos políticos y municipales.
        Tu tarea es extraer la lista de miembros de la corporación municipal (concejales, alcalde) Y contactos institucionales clave del siguiente texto.

        Para cada entrada encontrada, extrae:
        - "nombre": Nombre completo de la persona O nombre del departamento/área (ej: "Juan Pérez", "Área de Cultura", "Alcaldía").
        - "partido": Partido político (siglas o nombre) solo si es una persona vinculada a uno.
        - "cargo": Cargo o función (ej: "Alcalde", "Concejal de Fiestas", "Oficina de Atención Ciudadana").
        - "email": Email de contacto directo o institucional.
        - "tipo": Clasifica como "Persona" (si es un individuo con nombre propio) o "Organización/Departamento" (si es un contacto genérico de área).

        Si no encuentras información relevante, devuelve una lista vacía [].
        Devuelve ÚNICAMENTE un JSON válido con una lista de objetos bajo la clave "data". Sin texto adicional ni bloques de código markdown.

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
