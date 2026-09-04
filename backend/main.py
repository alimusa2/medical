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

# Include API Routers (register under /api, /<router>, and root prefixes for 100% serverless path matching)
router_configs = [
    ("/api/documents", "/documents", "", documents.router),
    ("/api/evaluations", "/evaluations", "", evaluations.router),
    ("/api/standards", "/standards", "", standards.router),
    ("/api/reports", "/reports", "", reports.router),
    ("/api/certifier", "/certifier", "", certifier.router),
    ("/api/settings", "/settings", "", settings_router.router),
    ("/api/samples", "/samples", "", samples.router),
]

for p1, p2, p3, r in router_configs:
    app.include_router(r, prefix=p1)
    app.include_router(r, prefix=p2)
    if p3 is not None:
        app.include_router(r, prefix=p3)





# Vercel Path Rewrite Middleware (restores original request path from Vercel headers)
@app.middleware("http")
async def vercel_path_rewrite_middleware(request, call_next):
    original_path = request.headers.get("x-matched-path") or request.headers.get("x-forwarded-uri")
    if original_path and original_path != request.url.path:
        clean_path = original_path.split("?")[0]
        request.scope["path"] = clean_path
    response = await call_next(request)
    return response

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
