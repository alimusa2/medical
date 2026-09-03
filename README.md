# MedVerify AI — Medical Device Test Report Evaluation Assistant

> **PROTOTYPE / PROOF-OF-CONCEPT SYSTEM**  
> ⚠️ **IMPORTANT DISCLAIMER**: Final technical review and certification remain the sole responsibility of qualified human personnel. Synthetic demonstration data and criteria are used throughout. This platform is not a certified medical-device evaluation system nor an official IEC compliance engine.

---

## 1. Project Overview

**MedVerify AI** is an enterprise proof-of-concept platform designed for medical electrical equipment testing companies. It automates repetitive technical reviewer tasks by:

1. **Processing Multi-Format TRFs**: Accepts PDF, CSV, XLSX, and DOCX Test Report Forms.
2. **Extracting Technical Data**: Extracts device metadata, applicable standards, test names, observed values, and technician evidence.
3. **Standards-Driven Deterministic Engine**: Runs pure Python numerical (`<=`, `>=`, ranges) and categorical rule evaluation against configured demonstration requirements (e.g., IEC 60601-1 demo criteria).
4. **Three-State Compliance Logic**: Strictly classifies results as **PASS**, **FAIL**, or **NEEDS REVIEW**. Uncertain, unmapped, missing, or expert-judgment parameters resolve to **NEEDS REVIEW**.
5. **AI-Assisted Summarization**: Uses Groq LLM API (`openai/gpt-oss-120b` or active fallback models) to structure JSON summaries without overriding deterministic PASS/FAIL rules.
6. **ReportLab PDF Generation**: Generates color-coded PDF Evaluation Reports with cover page, test findings matrix, AI executive summary, legal disclaimers, and human sign-off blocks.
7. **Certifier Handoff Workflow**: Provides a certifier queue interface with Approve, Request Technical Info, and Return to Reviewer actions.

---

## 2. System Architecture

```text
                                    +-----------------------------------------+
                                    |     React + Vite + Tailwind CSS UI      |
                                    |  (Dashboard, Upload, Document Review,   |
                                    |   Evaluations, Standards, Certifier)    |
                                    +--------------------+--------------------+
                                                         |
                                                         | HTTP / REST API (Port 8000)
                                                         v
                                    +--------------------+--------------------+
                                    |         FastAPI Backend Server          |
                                    |            (Python 3.10+)               |
                                    +---------+----------+----------+---------+
                                              |          |          |
                      +-----------------------+          |          +-----------------------+
                      v                                  v                                  v
+---------------------+-------------------+    +---------+--------+             +-----------+-----------+
|    Document Extraction Pipeline         |    | Deterministic    |             |  Groq AI Integration      |
| PyMuPDF / pdfplumber / Pandas / python-docx| | Evaluation Engine|             | (LLM Structuring, Mapping |
+-----------------------------------------+    | (Python Logic)   |             |  & Report Summarization)  |
                                               +------------------+             +-----------------------+
                                                         |
                                                         v
                                               +------------------+
                                               | SQLite Database  |
                                               | (medverify.db)   |
                                               +------------------+
```

---

## 3. Technology Stack

- **Backend**: Python 3.10+, FastAPI, SQLAlchemy, SQLite, Pydantic V2, PyMuPDF (`fitz`), `pdfplumber`, `pandas`, `openpyxl`, `python-docx`, `reportlab`, `pytest`.
- **Frontend**: React 18, Vite, Tailwind CSS, Lucide React icons, Recharts, Axios, React Router v6.
- **AI Integration**: Groq API (`groq` SDK) with `openai/gpt-oss-120b` (fallback models: `llama-3.3-70b-versatile`, `mixtral-8x7b-32768`).

---

## 4. Repository Structure

```text
├── backend/
│   ├── main.py                   # FastAPI application entrypoint & startup seeder
│   ├── config.py                 # Environment settings & directory creation
│   ├── database.py               # SQLAlchemy engine & session manager
│   ├── models.py                 # SQLAlchemy DB models
│   ├── schemas.py                # Pydantic schemas & normalized TRF structure
│   ├── seed_data.py              # DB seeder & synthetic demo TRF file generator
│   ├── services/
│   │   ├── document_processor.py # PDF, CSV, XLSX, DOCX extraction pipeline
│   │   ├── evaluation_engine.py  # Pure Python deterministic evaluation engine
│   │   ├── ai_service.py         # Groq LLM integration & fallback handler
│   │   └── report_generator.py   # ReportLab PDF report builder
│   ├── routers/
│   │   ├── documents.py          # TRF file upload & raw data inspection APIs
│   │   ├── evaluations.py        # Evaluation execution & result retrieval APIs
│   │   ├── standards.py          # Standards & requirements management APIs
│   │   ├── reports.py            # PDF report listing & download APIs
│   │   ├── certifier.py          # Certifier queue & action APIs
│   │   ├── settings.py           # Health check, Groq model test, & reseed APIs
│   │   └── samples.py            # Downloadable synthetic TRFs endpoint
│   ├── tests/
│   │   └── test_evaluation_engine.py # Pytest automated test suite (6 test cases)
│   ├── requirements.txt
│   └── .env
└── frontend/
    ├── package.json
    ├── vite.config.js
    ├── tailwind.config.js
    ├── index.html
    └── src/
        ├── App.jsx               # React Router & Layout wrapper
        ├── main.jsx              # React root entrypoint
        ├── index.css             # Tailwind imports & custom enterprise styling
        ├── components/           # Sidebar, Header, StatusBadge, ConfidenceBadge, etc.
        ├── pages/                # Dashboard, UploadPage, DocumentReviewPage, etc.
        └── services/api.js       # Axios API client
```

---

## 5. Environment Configuration

The backend reads configuration from `backend/.env`:

```env
GROQ_API_KEY=your_groq_api_key_here
GROQ_MODEL=openai/gpt-oss-120b
DATABASE_URL=sqlite:///./medverify.db
UPLOAD_DIR=./uploads
REPORT_DIR=./reports
SAMPLE_DIR=./samples
```

---

## 6. Installation & Quick Start

### Backend Setup

```bash
cd backend
python -m venv venv
# On Windows PowerShell:
.\venv\Scripts\Activate.ps1
# On Linux/macOS:
source venv/bin/activate

pip install -r requirements.txt
python main.py
```
The FastAPI backend runs on `http://localhost:8000`. API Documentation is available at `http://localhost:8000/docs`.

### Frontend Setup

```bash
cd frontend
cmd /c "npm install"
cmd /c "npm run dev"
```
The React Vite frontend application will start on `http://localhost:5173`.

---

## 7. How to Test the Complete End-to-End Workflow

1. **Start Backend & Frontend**: Launch FastAPI on port 8000 and Vite on port 5173.
2. **Open Dashboard**: Navigate to `http://localhost:5173`. Notice the pre-seeded metrics and quick sample download buttons.
3. **Download Demo Synthetic TRFs**: Click the sample download links on the Dashboard to download:
   - `demo_blood_pressure_PASS.pdf` (All criteria satisfy demo limits)
   - `demo_blood_pressure_FAIL.pdf` (Fails leakage current & temperature thresholds)
   - `demo_blood_pressure_NEEDS_REVIEW.pdf` (Missing insulation value & unmapped parameter)
4. **Upload TRF**: Navigate to **Upload Document** and drag & drop `demo_blood_pressure_PASS.pdf` or `demo_blood_pressure_FAIL.pdf`.
5. **Observe Pipeline Visualizer**: Watch the real-time stage progress: `Uploading` -> `Extracting` -> `Analyzing` -> `Mapping` -> `Evaluating` -> `Generating Report`.
6. **Inspect Evaluation Results**:
   - View overall compliance banner (`PASS`, `FAIL`, `NEEDS REVIEW`).
   - Examine itemized test results with status badges and AI mapping confidence scores.
   - Click any row to view the detailed failure rationale drawer.
   - Read the Groq AI-generated executive summary.
7. **Generate & Download PDF Report**: Click **Generate PDF Report** -> **Download PDF Report** to view the formatted PDF evaluation document.
8. **Certifier Decision Workflow**: Click **Submit to Certifier** -> Navigate to **Certifier Queue** -> Perform **Approve Evaluation**, **Request Technical Info**, or **Return to Reviewer**.
9. **Run Automated Tests**:
   ```bash
   cd backend
   python -m pytest tests/test_evaluation_engine.py
   ```
# medical
