import os
import sys

# Add the backend directory to the Python path so imports resolve correctly
backend_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend"))
sys.path.insert(0, backend_path)

# Export the FastAPI app so Vercel can find it
from app.main import app
