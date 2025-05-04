"""
    API routers package
"""

from .entities.route import entity_router
from .nlp_entities.route import nlp_entity_router

__all__ = [
    "entity_router",
    "nlp_entity_router",
]
