"""
    Este archivo contiene las rutas relacionadas con la autenticación de usuarios.
"""

from fastapi import APIRouter

router = APIRouter(
    prefix="/api/auth",  # Todas las rutas aquí empiezan con /api/auth
    tags=["Autenticación"]
)

@router.post("/login")
async def login():
    """
        Login route
    """
    return {"message": "Login exitoso"}

@router.post("/register")
async def register():
    """
        Register route
    """
    return {"message": "Registro exitoso"}
