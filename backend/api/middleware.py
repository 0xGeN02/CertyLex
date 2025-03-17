"""
Middleware for the API
"""
import os
from typing import List
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

load_dotenv()
app = FastAPI()

NEXTJS_URL: str = os.getenv("NEXTJS_URL", "http:/localhost/3000")
FASTAPI_URL: str = os.getenv("FASTAPI_URL", "http:/localhost/5328")

# Allowed IP addresses
ALLOWED_IPS: List[str] = [
    NEXTJS_URL,
    FASTAPI_URL,
]

# Add the middleware to the FastAPI application
app.add_middleware = CORSMiddleware(
    app=app,
    allow_origins=ALLOWED_IPS,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
    allow_credentials=True,
)
