"""
Logging centralizado (Fase 10 -- observabilidade).
"""
import logging


def get_logger(name: str) -> logging.Logger:
    logging.basicConfig(level=logging.INFO)
    return logging.getLogger(name)
