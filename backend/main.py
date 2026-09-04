import sys
import os

# Ensure backend directory is in sys.path before any sibling imports
backend_dir = os.path.dirname(os.path.abspath(__file__))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

try:
    from database import engine, Base, SessionLocal
    from seed_data import seed_database
    from config import settings
    from routers import documents, evaluations, standards, reports, certifier, settings as settings_router, samples
except ImportError:
    from backend.database import engine, Base, SessionLocal
    from backend.seed_data import seed_database
    from backend.config import settings
    from backend.routers import documents, evaluations, standards, reports, certifier, settings as settings_router, samples

# Initialize database schema safely
try:
    Base.metadata.create_all(bind=engine)
    from models import Standard
    db = SessionLocal()
    if db.query(Standard).first() is None:
        print("Initial database setup: seeding standards and synthetic sample TRFs...")
        seed_database(db)
        print("Database initial seeding complete.")
    else:
        print("Database schema and standards ready.")
    db.close()
except Exception as e:
    print(f"Warning during startup database initialization: {e}")

app = FastAPI(
    title="MedVerify AI API",
    description="Medical Device Test Report Evaluation Assistant - Proof of Concept",
    version="1.0.0"
)

# Configure CORS for frontend Vite dev server
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API Routers cleanly (registered under /api and /<name> prefixes)
routers = [
    ("/api/documents", "/documents", documents.router),
    ("/api/evaluations", "/evaluations", evaluations.router),
    ("/api/standards", "/standards", standards.router),
    ("/api/reports", "/reports", reports.router),
    ("/api/certifier", "/certifier", certifier.router),
    ("/api/settings", "/settings", settings_router.router),
    ("/api/samples", "/samples", samples.router),
]

for p1, p2, r in routers:
    app.include_router(r, prefix=p1)
    app.include_router(r, prefix=p2)






# Vercel Path Rewrite Middleware (restores original request path from Vercel query string/headers)
@app.middleware("http")
async def vercel_path_rewrite_middleware(request, call_next):
    q_path = request.query_params.get("path")
    matched_header = request.headers.get("x-matched-path")
    
    real_path = None
    if q_path:
        real_path = "/" + q_path.lstrip("/")
    elif matched_header and matched_header not in ["/api/index.py", "/", "/index.py"]:
        real_path = matched_header

    if real_path:
        request.scope["path"] = real_path

    if request.scope.get("path") in ["/debug-routes", "/api/debug-routes"]:
        from starlette.responses import JSONResponse
        return JSONResponse({
            "method": request.method,
            "raw_path": request.url.path,
            "scope_path": request.scope.get("path"),
            "headers": {k.decode("latin1"): v.decode("latin1") for k, v in request.scope.get("headers", [])},
            "routes": [getattr(r, "path", str(r)) for r in app.routes]
        })

    return await call_next(request)

from starlette.routing import Match
from fastapi import Request

# Explicit Vercel Serverless Index Handler (dispatches rewritten POST/GET requests to target routes)
@app.api_route("/api/index.py", methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "HEAD", "PATCH"])
@app.api_route("/index.py", methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "HEAD", "PATCH"])
async def vercel_index_handler(request: Request):
    q_path = request.query_params.get("__path__") or request.query_params.get("path")
    matched_header = request.headers.get("x-matched-path") or request.headers.get("x-forwarded-uri")
    
    target_path = q_path or matched_header or "/"
    clean_target = "/" + target_path.lstrip("/")
    
    if clean_target in ["/", "/api", "/api/", "/api/index.py", "/index.py"]:
        return {
            "app": "MedVerify AI",
            "status": "online",
            "disclaimer": "DEMONSTRATION DATA ONLY — NOT FOR OFFICIAL MEDICAL DEVICE CERTIFICATION USE",
            "docs_url": "/docs"
        }
        
    scope = dict(request.scope)
    scope["path"] = clean_target
    
    for route in app.routes:
        if hasattr(route, "matches") and route.path not in ["/api/index.py", "/index.py"]:
            match, _ = route.matches(scope)
            if match == Match.FULL:
                return await route.handle(scope, request._receive, request._send)

    return {
        "app": "MedVerify AI",
        "status": "online",
        "disclaimer": "DEMONSTRATION DATA ONLY — NOT FOR OFFICIAL MEDICAL DEVICE CERTIFICATION USE",
        "docs_url": "/docs"
    }

@app.get("/")
@app.get("/api")
@app.get("/api/")
def root():
    return {
        "app": "MedVerify AI",
        "status": "online",
        "disclaimer": "DEMONSTRATION DATA ONLY — NOT FOR OFFICIAL MEDICAL DEVICE CERTIFICATION USE",
        "docs_url": "/docs"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
