"""
    Include all the routes from the routes directory
"""

from .middleware import app
from .routers import (
    auth_router,
    boe_router,
)

# Incluir todos los routers
app.include_router(auth_router)
app.include_router(boe_router)
