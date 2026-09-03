from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
import os

from backend.database import init_db
from backend.seed_data import seed_database
from backend.routers import incidents, recommendations, analytics, events, system, ml

app = FastAPI(
    title="Verified Resolution Assistant API",
    description="Evidence-backed resolution retrieval for 24/7 clinical IT support",
    version="1.0.0"
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Set up paths
BASE_DIR = Path(__file__).parent.parent
STATIC_DIR = BASE_DIR / "static"
TEMPLATES_DIR = BASE_DIR / "templates"

# Create directories if missing
STATIC_DIR.mkdir(parents=True, exist_ok=True)
TEMPLATES_DIR.mkdir(parents=True, exist_ok=True)

# Mount static directory
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

# Include Routers
app.include_router(incidents.router)
app.include_router(recommendations.router)
app.include_router(analytics.router)
app.include_router(events.router)
app.include_router(system.router)
app.include_router(ml.router)

@app.on_event("startup")
def on_startup():
    db_file = BASE_DIR / "hospital_it.db"
    if not db_file.exists():
        print("Database not found. Initializing and seeding synthetic hospital IT data...")
        seed_database()
    else:
        print(f"Connected to database at {db_file}")

@app.get("/", response_class=FileResponse)
def serve_index():
    return FileResponse(str(TEMPLATES_DIR / "index.html"))

@app.post("/api/seed")
def reseed_database_endpoint():
    seed_database()
    return {"message": "Database reseeded successfully with synthetic hospital IT data."}
