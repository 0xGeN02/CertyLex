"""
    API routers package
"""

from .auth.route import router as auth_router
from .boe.route import router as boe_router

__all__ = [
    "auth_router",
    "boe_router",
]
