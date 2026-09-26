import os
import uvicorn
import sys
from pathlib import Path

# Add backend directory to sys.path
backend_dir = Path(__file__).resolve().parent
sys.path.insert(0, str(backend_dir))

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    reload_flag = os.environ.get("ENVIRONMENT", "").lower() != "production"
    print(f"[INFO] Launching NeighbourFlex FastAPI Backend on port {port} (reload={reload_flag}) ...")
    uvicorn.run("app.main:app", host="0.0.0.0", port=port, reload=reload_flag, reload_dirs=[str(backend_dir)] if reload_flag else None)

