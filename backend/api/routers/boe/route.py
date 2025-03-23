"""
    Router for the BOE api section
"""

from fastapi import APIRouter

router = APIRouter(
    prefix="/api/boe",
    tags=["BOE"],
)

@router.get("/")
async def root():
    """
        Root route for the BOE API section
    """
    return {"message": "Welcome to the BOE API section!"}
