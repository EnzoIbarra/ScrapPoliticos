"""
Sistema de retry con backoff exponencial
"""

import time
from functools import wraps
from typing import Callable, Any

from core.logger import get_logger

logger = get_logger(__name__)

def retry_with_fallback(max_retries: int = 3, backoff: int = 2):
    """
    Decorator para reintentos automáticos con backoff exponencial.
    
    Args:
        max_retries: Número máximo de reintentos
        backoff: Factor de backoff (tiempo = backoff ** intento)
    
    Returns:
        Decorator function
        
    Example:
        @retry_with_fallback(max_retries=3, backoff=2)
        def fetch_data(url):
            return requests.get(url)
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                    
                except Exception as e:
                    # GESTIÓN DE FALLOS (Incluye errores de Proxy):
                    # Si Tor o la conexión directa fallan (ProxyError, 503, etc.),
                    # el sistema pausará la ejecución y reintentará automáticamente
                    # hasta agotar el número máximo de intentos.
                    
                    # Último intento, propagar error
                    if attempt == max_retries - 1:
                        logger.error(f"{func.__name__} falló después de {max_retries} intentos: {e}")
                        raise
                    
                    # Calcular tiempo de espera
                    wait_time = backoff ** attempt
                    logger.warning(
                        f"{func.__name__} falló (intento {attempt + 1}/{max_retries}). "
                        f"Reintentando en {wait_time}s... Error: {e}"
                    )
                    time.sleep(wait_time)
            
        return wrapper
    return decorator
