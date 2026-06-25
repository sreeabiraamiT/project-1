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
    allow_origins=[
    "https://eb-billanalyzer.netlify.app",
    "http://localhost:5173"
],
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
if __name__ == "__main__":
    # Read the dynamic PORT variable given by Render, default to 8000 locally
    port = int(os.environ.get("PORT", 8000))
    
    # CRUCIAL: Must bind to host "0.0.0.0" so Render can find it
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=False)
