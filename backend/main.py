import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from database import engine, Base, SessionLocal
from seed_data import seed_database
from config import settings

from routers import documents, evaluations, standards, reports, certifier, settings as settings_router, samples

# Initialize database schema
Base.metadata.create_all(bind=engine)

# Seed database on startup only if uninitialized
try:
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

# Include API Routers
app.include_router(documents.router)
app.include_router(evaluations.router)
app.include_router(standards.router)
app.include_router(reports.router)
app.include_router(certifier.router)
app.include_router(settings_router.router)
app.include_router(samples.router)

@app.get("/")
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
