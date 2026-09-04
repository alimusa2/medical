import sys
import os
import traceback
from urllib.parse import parse_qs

# Ensure backend directory and root directory are in sys.path
current_dir = os.path.dirname(os.path.abspath(__file__))
backend_dir = os.path.dirname(current_dir)
root_dir = os.path.dirname(backend_dir)

for d in [backend_dir, root_dir, current_dir]:
    if os.path.exists(d) and d not in sys.path:
        sys.path.insert(0, d)

# Set VERCEL environment flag
os.environ["VERCEL"] = "1"

class VercelPathRewriteASGI:
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] == "http":
            query_string = scope.get("query_string", b"").decode("utf-8")
            qs = parse_qs(query_string)
            path_param = qs.get("path", [None])[0]

            if path_param:
                scope["path"] = "/" + path_param.lstrip("/")
            else:
                headers = dict(scope.get("headers", []))
                matched_header = headers.get(b"x-matched-path", b"").decode("utf-8")
                if matched_header and matched_header not in ["/api/index.py", "/", "/index.py"]:
                    scope["path"] = matched_header

        await self.app(scope, receive, send)

try:
    import main
    app = VercelPathRewriteASGI(main.app)
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
