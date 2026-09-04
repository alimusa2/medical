import sys
import os
import traceback
from urllib.parse import parse_qs

current_dir = os.path.dirname(os.path.abspath(__file__))
backend_dir = os.path.dirname(current_dir)
root_dir = os.path.dirname(backend_dir)

for d in [backend_dir, root_dir, current_dir]:
    if os.path.exists(d) and d not in sys.path:
        sys.path.insert(0, d)

os.environ["VERCEL"] = "1"

class VercelPathRewriteASGI:
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] == "http":
            query_string = scope.get("query_string", b"").decode("utf-8")
            qs = parse_qs(query_string)
            path_param = qs.get("__path__", [None])[0] or qs.get("path", [None])[0]

            headers = dict(scope.get("headers", []))
            forwarded_uri = headers.get(b"x-forwarded-uri", b"").decode("utf-8")
            original_url = headers.get(b"x-original-url", b"").decode("utf-8")

            real_path = path_param or forwarded_uri or original_url
            if real_path:
                clean_path = real_path.split("?")[0]
                scope["path"] = "/" + clean_path.lstrip("/")

        await self.app(scope, receive, send)

try:
    import main
    app = VercelPathRewriteASGI(main.app)
except Exception as e:
    err_msg = str(e)
    err_trace = traceback.format_exc()
    print(f"[VERCEL INITIALIZATION ERROR]: {err_trace}")
    
    from starlette.responses import JSONResponse
    
    class ErrorApp:
        async def __call__(self, scope, receive, send):
            resp = JSONResponse({
                "status": "error",
                "message": "Backend module import failed during serverless startup",
                "error": err_msg,
                "traceback": err_trace.splitlines()
            }, status_code=500)
            await resp(scope, receive, send)
            
    app = ErrorApp()
