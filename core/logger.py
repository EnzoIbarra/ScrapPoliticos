"""
Sistema de logging estructurado para ScrapPoliticos
"""

import logging
import os
from pathlib import Path

# Crear directorio de logs si no existe
LOGS_DIR = Path(__file__).parent.parent / 'logs'
LOGS_DIR.mkdir(exist_ok=True)

# Formato de logs
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
DATE_FORMAT = '%Y-%m-%d %H:%M:%S'

def get_logger(name: str) -> logging.Logger:
    """
    Obtiene un logger configurado para un módulo.
    
    Args:
        name: Nombre del módulo (__name__)
    
    Returns:
        Logger configurado
    """
    logger = logging.getLogger(name)
    
    # Si ya está configurado,  retornar
    if logger.handlers:
        return logger
    
    logger.setLevel(logging.DEBUG)
    
    # Handler para archivo
    file_handler = logging.FileHandler(
        LOGS_DIR / 'scraper.log',
        encoding='utf-8'
    )
    file_handler.setLevel(logging.DEBUG)
    file_formatter = logging.Formatter(LOG_FORMAT, DATE_FORMAT)
    file_handler.setFormatter(file_formatter)
    
    # Handler para consola
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_formatter = logging.Formatter('%(levelname)s - %(message)s')
    console_handler.setFormatter(console_formatter)
    
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger
