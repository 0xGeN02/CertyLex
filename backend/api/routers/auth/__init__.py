""""
    Authentication and authorization router for FastAPI.
"""

from .route import router as auth_router

__all__ = [
    "auth_router",
]
# The __all__ variable is a convention in Python that defines the public interface of a module.
# It is a list of strings that represent the names of the objects (functions, classes, variables, etc.) that should be accessible when the module is imported using the from module import * syntax.
# By defining __all__, you can control what is exported from the module and prevent accidental exposure of internal implementation details.
