"""
api/index.py — Vercel serverless entry point for the FastAPI application.
Vercel looks for a file in api/ directory and expects an ASGI app variable named 'app'.
"""
import sys
import os

# Ensure the project root is on the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.main import app  # noqa: F401 — Vercel picks up 'app' from here
