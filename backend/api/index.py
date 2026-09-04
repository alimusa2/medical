import sys
import os
import traceback

current_dir = os.path.dirname(os.path.abspath(__file__))
backend_dir = os.path.dirname(current_dir)
root_dir = os.path.dirname(backend_dir)

for d in [backend_dir, root_dir, current_dir]:
    if os.path.exists(d) and d not in sys.path:
        sys.path.insert(0, d)

os.environ["VERCEL"] = "1"

sys.stderr.write(f"[VERCEL STARTUP] Python version: {sys.version}\n")

try:
    import main
    app = main.app
    sys.stderr.write("[VERCEL STARTUP] Successfully imported main.app!\n")
except Exception as e:
    err_trace = traceback.format_exc()
    sys.stderr.write(f"[VERCEL STARTUP FAILED]: {err_trace}\n")
    
    from starlette.responses import PlainTextResponse
    class FatalApp:
        async def __call__(self, scope, receive, send):
            resp = PlainTextResponse(f"BACKEND INITIALIZATION FAILED:\n\n{err_trace}", status_code=500)
            await resp(scope, receive, send)
    app = FatalApp()
