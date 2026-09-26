import uvicorn
import sys
from pathlib import Path

# Add backend directory to sys.path
backend_dir = Path(__file__).resolve().parent
sys.path.insert(0, str(backend_dir))

if __name__ == "__main__":
    print("[INFO] Launching NeighbourFlex FastAPI Backend on http://127.0.0.1:8000 ...")
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True, reload_dirs=[str(backend_dir)])
