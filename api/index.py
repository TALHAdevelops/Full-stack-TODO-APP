"""
Vercel serverless function entry point for FastAPI.
According to Vercel's Python runtime docs, the entry point must be in an 'api' directory.
"""

import sys
from pathlib import Path

# Add parent directory to path so we can import backend
parent_path = Path(__file__).parent.parent
backend_path = parent_path / "backend"

if str(backend_path) not in sys.path:
    sys.path.insert(0, str(backend_path))

# Import the FastAPI app from backend/main.py
# The file should be named app.py for Vercel to auto-detect, or we export 'app' variable
import main

# Vercel looks for 'app' or 'handler' as the ASGI application
app = main.app
