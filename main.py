from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import engine, Base
import models
import upload, tips, history
from dotenv import load_dotenv

# Load .env variables right at startup so Gemini SDK can access the API key
load_dotenv()

app = FastAPI(
    title="Electricity Bill Analyser API",
    description="Unified API for OCR text extraction, appliance estimation, and AI savings tips",
    version="1.0"
)

# This prevents browsers from blocking your frontend requests (CORS errors)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8000", "http://localhost:5173"],  # your actual frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Automatically builds SQLite or PostgreSQL tables if they don't exist yet
Base.metadata.create_all(bind=engine)

# Include core feature routers (services.py is imported inside upload.py, not here)
app.include_router(upload.router, tags=["Upload"])
app.include_router(history.router, tags=["History"])
app.include_router(tips.router, tags=["Tips"])


@app.get("/Connection")
def Connection():
    """
    Checks if the database connection pool is active and operational.
    """
    try:
        con = engine.connect()
        con.close()
        return "Connected"
    except Exception:
        return "Failed"


@app.get("/")
def home():
    """
    Root landing response message.
    """
    return "Electricity bill analyser"
