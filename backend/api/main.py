"""
Main file for the FastAPI application
"""
import os
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse

app = FastAPI()
API_ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
FAVICON_PATH = os.path.join(API_ROOT_DIR, "favicon.ico")

@app.get("/")
async def home():
    """
    Home page of the API
    """
    return {"message": "Hello, FastAPI!"}

@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    """
    Return the favicon
    """
    if not os.path.exists(FAVICON_PATH):
        raise HTTPException(status_code=404, detail="Favicon not found")
    return FileResponse(FAVICON_PATH)

@app.get("/api")
async def api_root():
    """
    Root of the API
    """
    return {"message": "Hello from FastAPI /api route!"}
