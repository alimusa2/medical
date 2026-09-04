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

from starlette.types import ASGIApp, Scope, Receive, Send
from urllib.parse import parse_qs

class VercelPathRewriteASGIMiddleware:
    def __init__(self, app: ASGIApp):
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send):
        if scope["type"] == "http":
            query_string = scope.get("query_string", b"").decode("utf-8", errors="ignore")
            qs = parse_qs(query_string)
            
            q_path = None
            if "__path__" in qs and qs["__path__"]:
                q_path = qs["__path__"][0]
            elif "path" in qs and qs["path"]:
                q_path = qs["path"][0]

            headers = dict(scope.get("headers", []))
            x_uri = headers.get(b"x-forwarded-uri", b"").decode("utf-8", errors="ignore")
            x_match = headers.get(b"x-matched-path", b"").decode("utf-8", errors="ignore")

            matched_header = None
            for h in [x_uri, x_match]:
                if h and h not in ["/api/index.py", "/index.py", "/", "/api", "/api/"]:
                    matched_header = h
                    break

            real_path = None
            if q_path:
                real_path = "/" + q_path.lstrip("/")
            elif matched_header:
                real_path = "/" + matched_header.lstrip("/")

            if real_path and real_path not in ["/api/index.py", "/index.py"]:
                scope["path"] = real_path

        await self.app(scope, receive, send)

# Configure CORS for frontend Vite dev server
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(VercelPathRewriteASGIMiddleware)

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

    # 1. Samples Direct Route
    if "samples" in clean_target:
        from database import SessionLocal
        try:
            from routers.samples import list_sample_trfs, download_sample_trf, run_sample_evaluation
        except ImportError:
            from backend.routers.samples import list_sample_trfs, download_sample_trf, run_sample_evaluation
        
        db = SessionLocal()
        try:
            if "download" in clean_target and request.method in ["GET", "HEAD"]:
                filename = clean_target.split("/")[-1]
                return download_sample_trf(filename=filename, db=db)
            elif "run-sample" in clean_target and request.method in ["POST", "OPTIONS"]:
                filename = clean_target.split("/")[-1]
                return run_sample_evaluation(filename=filename, db=db)
            elif request.method in ["GET", "HEAD"]:
                return list_sample_trfs(db=db)
        finally:
            db.close()

    # 2. Document Upload & List Direct Route
    if "upload" in clean_target and request.method in ["POST", "OPTIONS"]:
        from database import SessionLocal
        try:
            from routers.documents import upload_document
        except ImportError:
            from backend.routers.documents import upload_document
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

    if "documents" in clean_target and request.method in ["GET", "HEAD"]:
        from database import SessionLocal
        try:
            from routers.documents import list_documents
        except ImportError:
            from backend.routers.documents import list_documents
        db = SessionLocal()
        try:
            return list_documents(db=db)
        finally:
            db.close()

    # 3. Run Evaluation & List Direct Route
    if "evaluations" in clean_target:
        from database import SessionLocal
        try:
            from routers.evaluations import run_evaluation, list_evaluations
        except ImportError:
            from backend.routers.evaluations import run_evaluation, list_evaluations
        db = SessionLocal()
        try:
            if "run" in clean_target and request.method in ["POST", "OPTIONS"]:
                import re
                m = re.search(r"document/(\d+)/run", clean_target)
                if m:
                    doc_id = int(m.group(1))
                    return run_evaluation(doc_id=doc_id, db=db)
            elif request.method in ["GET", "HEAD"]:
                return list_evaluations(db=db)
        finally:
            db.close()

    # 4. Default Root Info Response
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
