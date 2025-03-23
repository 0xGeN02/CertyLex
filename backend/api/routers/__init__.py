"""
    API routers package
"""

from .auth import auth_router
from .boe import boe_router

__all__ = [
    "auth_router",
    "boe_router",
]
