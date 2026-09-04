import os
from typing import List
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from config import settings

router = APIRouter(tags=["reports"])

@router.get("")
def list_generated_reports():
    report_files = []
    if os.path.exists(settings.REPORT_DIR):
        for fname in os.listdir(settings.REPORT_DIR):
            if fname.endswith(".pdf"):
                fpath = os.path.join(settings.REPORT_DIR, fname)
                stat = os.stat(fpath)
                report_files.append({
                    "filename": fname,
                    "size_bytes": stat.st_size,
                    "created_at": stat.st_ctime,
                    "download_url": f"/api/reports/{fname}/download"
                })
    return sorted(report_files, key=lambda x: x["created_at"], reverse=True)

@router.get("/{filename}/download")
def download_report(filename: str):
    file_path = os.path.join(settings.REPORT_DIR, filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Requested PDF report file not found")
    return FileResponse(file_path, media_type="application/pdf", filename=filename)
