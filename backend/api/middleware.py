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

NEXTJS_URL: str = os.getenv("NEXTJS_URL")
FASTAPI_URL: str = os.getenv("FASTAPI_URL")

# Allowed IP addresses
ALLOWED_IPS: List[str] = [
    NEXTJS_URL,
    FASTAPI_URL,
    "http://localhost:3000",  # DEV NEXTJS backup url
    "http://localhost:5328"   # DEV FASTAPI backup url
]

ALLOWED_METHODS: List[str] = [
    "GET",
    "POST",
    "PUT",
    "DELETE",
    "OPTIONS"
]

ALLOWED_HEADERS: List[str] = [
    "Origin",
    "Authorization",
    "Content-Type",
    "Accept",
    "X-Requested-With"
]

# Add the middleware to the FastAPI application
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_IPS,
    allow_credentials=True,
    allow_methods=ALLOWED_METHODS,     # Use ["*"] for dev or testing
    allow_headers=ALLOWED_HEADERS      # Use ["*"] for dev or testing
)

@app.get("/middleware")
def middleware_root():
    """
    Root of the middleware
    """
    return {"message": "Hello from FastAPI Middleware!"}

@app.get("/middleware/allowed_ips")
def get_allowed_ips():
    """
    Get the allowed IPs
    """
    return {"allowed_ips": ALLOWED_IPS}
