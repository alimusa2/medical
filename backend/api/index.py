import sys
import os
import traceback

# Ensure sys.path includes backend and api directories
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)

for d in [current_dir, parent_dir]:
    if os.path.exists(d) and d not in sys.path:
        sys.path.insert(0, d)

# Set VERCEL environment flag
os.environ["VERCEL"] = "1"

try:
    from main import app
except Exception as e:
    err_msg = str(e)
    err_trace = traceback.format_exc()
    print(f"[VERCEL INITIALIZATION ERROR]: {err_trace}")
    
    from fastapi import FastAPI
    app = FastAPI(title="MedVerify AI API (Diagnostic)")
    
    @app.api_route("/{full_path:path}", methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "HEAD", "PATCH"])
    def catch_all(full_path: str):
        return {
            "status": "error",
            "message": "Backend module import failed during serverless startup",
            "error": err_msg,
            "traceback": err_trace.splitlines()[-10:]
        }
