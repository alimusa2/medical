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

from fastapi import Request, Depends
from sqlalchemy.orm import Session
from database import get_db

# OPTIONS Preflight Interceptor Middleware
@app.middleware("http")
async def options_preflight_middleware(request: Request, call_next):
    if request.method == "OPTIONS":
        from starlette.responses import Response
        return Response(
            status_code=200,
            headers={
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "*",
                "Access-Control-Allow-Headers": "*",
            }
        )
    return await call_next(request)

# Priority Direct Serverless POST Endpoints (registered first to take precedence over GET routes)
@app.api_route("/api/documents/upload", methods=["POST", "OPTIONS"])
@app.api_route("/documents/upload", methods=["POST", "OPTIONS"])
@app.api_route("/upload", methods=["POST", "OPTIONS"])
async def direct_upload_document(request: Request):
    if request.method == "OPTIONS":
        from starlette.responses import Response
        return Response(status_code=200)
    from database import SessionLocal
    from routers.documents import upload_document
    db = SessionLocal()
    try:
        try:
            form = await request.form()
            file = form.get("file")
        except Exception:
            file = None

        if file:
            return await upload_document(file=file, db=db)
        else:
            from fastapi import HTTPException
            raise HTTPException(status_code=400, detail="No file found in form data")
    finally:
        db.close()

@app.api_route("/api/evaluations/document/{doc_id}/run", methods=["POST", "OPTIONS"])
@app.api_route("/evaluations/document/{doc_id}/run", methods=["POST", "OPTIONS"])
async def direct_run_evaluation(doc_id: int, request: Request, db: Session = Depends(get_db)):
    if request.method == "OPTIONS":
        from starlette.responses import Response
        return Response(status_code=200)
    from database import SessionLocal
    from routers.evaluations import run_evaluation
    db = SessionLocal()
    try:
        return run_evaluation(doc_id=doc_id, db=db)
    finally:
        db.close()

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

# Catch-all API Route for Vercel Serverless Function (handles GET, POST, OPTIONS for all routes)
@app.api_route("/{full_path:path}", methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "HEAD", "PATCH"])
@app.api_route("/api/index.py", methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "HEAD", "PATCH"])
@app.api_route("/index.py", methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "HEAD", "PATCH"])
async def vercel_catchall_handler(request: Request, full_path: str = ""):
    q_path = request.query_params.get("__path__") or request.query_params.get("path")
    matched_header = request.headers.get("x-forwarded-uri") or request.headers.get("x-matched-path")
    
    target_path = q_path or matched_header or full_path or request.url.path
    clean_target = "/" + target_path.lstrip("/")

    # 1. Document Upload Direct Route
    if "upload" in clean_target and request.method in ["POST", "OPTIONS"]:
        from database import SessionLocal
        from routers.documents import upload_document
        db = SessionLocal()
        try:
            try:
                form = await request.form()
                file = form.get("file")
            except Exception:
                file = None

            if file:
                return await upload_document(file=file, db=db)
            else:
                from fastapi import HTTPException
                raise HTTPException(status_code=400, detail="Please upload a TRF file using multipart form-data")
        finally:
            db.close()

    # 2. Run Evaluation Direct Route
    if "evaluations" in clean_target and "run" in clean_target and request.method in ["POST", "OPTIONS"]:
        from database import SessionLocal
        from routers.evaluations import run_evaluation
        db = SessionLocal()
        try:
            import re
            m = re.search(r"document/(\d+)/run", clean_target)
            if m:
                doc_id = int(m.group(1))
                return run_evaluation(doc_id=doc_id, db=db)
        finally:
            db.close()

    # 3. Default Root Info Response
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
